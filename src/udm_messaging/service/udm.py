import logging
from datetime import datetime
from typing import Optional

from shared.models import Message
from udm_messaging.port import UDMMessagingPort

import json

from ldap.controls.readentry import PostReadControl, PreReadControl

from univention.admin.rest.object import get_representation
import univention.admin.uldap
from univention.management.console.log import MODULE
from univention.management.console.modules.udm.udm_ldap import UDM_Module

logger = logging.getLogger(__name__)


class UDMMessagingService(univention.admin.uldap.access):
    def __init__(self, port: UDMMessagingPort):
        self._port = port

    async def retrieve(self, dn: str):
        return await self._port.retrieve(dn)

    async def store(self, new_obj: dict):
        await self._port.store(new_obj["dn"][0].decode(), json.dumps(new_obj))

    async def send_event(self, new_obj: Optional[dict], old_obj: Optional[dict]):
        object_type = new_obj["objectType"] if new_obj else old_obj["objectType"]

        message = Message(
            publisher_name="udm-listener",
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={"new": new_obj, "old": old_obj},
        )
        await self._port.send_event(message)

    async def resolve_references(self, obj: dict):
        fields_to_resolve = ("creatorsName", "modifiersName")
        for field in fields_to_resolve:
            value = obj[field]
            resolved_value = await self._port.get_object(f"users/user/{value}")
            obj[field] = resolved_value
        return obj

    def _get_module(self, object_type):
        module = UDM_Module(object_type, ldap_connection=self, ldap_position=None)
        if not module or not module.module:
            raise ModuleNotFound
        return module

    async def _handle_control_responses(self, responses):
        def _get_control(response, ctrl_type):
            for control in response.get("ctrls", []):
                if control.controlType == ctrl_type:
                    return control

        def _ldap_to_udm(raw):
            if raw is None:
                return None

            object_types = raw.entry.get("univentionObjectType", [])
            if not isinstance(object_types, list) or len(object_types) < 1:
                MODULE.warn("ReadControl response is missing `univentionObjectType`!")
                return None

            try:
                object_type = object_types[0].decode("utf-8")
                module = self._get_module(object_type)
                obj = module.module.object(
                    co=None,
                    lo=self,
                    position=None,
                    dn=raw.dn,
                    superordinate=None,
                    attributes=raw.entry,
                )
                obj.open()
                return get_representation(module, obj, ["*"], self, False)
            except ModuleNotFound:
                MODULE.error(
                    "ReadControl response has object type %r, but the module was not found!"
                    % object_type
                )
                return None

        if isinstance(responses, dict):
            responses = [responses]

        publish = []
        new = None
        old = None
        for response in responses:
            # extract control response and rebuild UDM representation
            topic = "n/a"
            new = _ldap_to_udm(_get_control(response, PostReadControl.controlType))
            new = await self.resolve_references(new)
            old = self.retrieve(
                new.get("uuid")
            )  # FIXME: find the way to retrieve old object without new (by UUID)
            await self.store(new)

            if old:
                topic = old["objectType"]
                MODULE.debug("UDM before change")
                for key, value in sorted(old.items(), key=lambda i: i[0]):
                    MODULE.debug(f"  {key}: {value}")
            if new:
                topic = new["objectType"]
                MODULE.debug("UDM after change")
                for key, value in sorted(new.items(), key=lambda i: i[0]):
                    MODULE.debug(f"  {key}: {value}")

            if old or new:
                publish.append((topic, old, new))
            else:
                MODULE.debug("No control responses for UDM objects were returned.")

        if publish:
            await self.send_event(new, old)

    def _extract_responses(self, func, response_name, *args, **kwargs):
        # Note: the original call must not pass `serverctrls` and/or `response` via `args`!

        # either re-use the given response dict, or provide our own
        if response_name not in kwargs:
            kwargs[response_name] = [] if response_name == "responses" else {}
        ctrl_response = kwargs.get(response_name)

        kwargs["serverctrls"] = [
            # strip the caller's Pre-/PostReadControls from the `serverctrls`
            control
            for control in (kwargs.get("serverctrls") or [])
            if control.controlType
            not in [PreReadControl.controlType, PostReadControl.controlType]
        ] + [
            # always add our all-inclusive Pre-/PostReadControls
            PreReadControl(False, ["*", "+"]),
            PostReadControl(False, ["*", "+"]),
        ]

        response = func(*args, **kwargs)
        self._handle_control_responses(ctrl_response)
        return response

    def add(self, *args, **kwargs):
        return self._extract_responses(super().add, "response", *args, **kwargs)

    def modify(self, *args, **kwargs):
        # If the DN and properties of the object are changed, this calls
        # ldap.rename_ext_s and ldap.modify_ext_s, yielding two responses.
        return self._extract_responses(super().modify, "responses", *args, **kwargs)

    def rename(self, *args, **kwargs):
        return self._extract_responses(super().rename, "response", *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._extract_responses(super().delete, "response", *args, **kwargs)


class ModuleNotFound(Exception):
    pass
