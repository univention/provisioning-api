import logging
from datetime import datetime
from typing import Optional

from shared.models import Message
from udm_messaging.port import UDMMessagingPort

import json
from univention.admin.rest.module import Object
import univention.admin.uldap
from univention.management.console.log import MODULE
from univention.management.console.modules.udm.udm_ldap import UDM_Module

logger = logging.getLogger(__name__)


class UDMMessagingService(univention.admin.uldap.access):
    def __init__(self, port: UDMMessagingPort):
        super().__init__(
            port=389,
            start_tls=0,
            base="dc=univention-organization,dc=intranet",
            binddn="cn=admin,dc=univention-organization,dc=intranet",
            bindpw="univention",
        )
        self._messaging_port = port

    async def retrieve(self, dn: str):
        return await self._messaging_port.retrieve(dn)

    async def store(self, new_obj: dict):
        await self._messaging_port.store(new_obj["dn"][0].decode(), json.dumps(new_obj))

    async def send_event(self, new_obj: Optional[dict], old_obj: Optional[dict]):
        object_type = new_obj["objectType"] if new_obj else old_obj["objectType"]

        message = Message(
            publisher_name="udm-listener",
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={"new": new_obj, "old": old_obj},
        )
        await self._messaging_port.send_event(message)

    async def resolve_references(self, obj: dict):
        fields_to_resolve = ("creatorsName", "modifiersName")
        for field in fields_to_resolve:
            value = obj[field]
            resolved_value = await self._messaging_port.get_object(
                f"users/user/{value}"
            )
            obj[field] = resolved_value
        return obj

    def _get_module(self, object_type):
        module = UDM_Module(object_type, ldap_connection=self, ldap_position=None)
        if not module or not module.module:
            raise ModuleNotFound
        return module

    async def _handle_control_responses(self, obj):
        def _ldap_to_udm(entry):
            if entry is None:
                return None

            object_types = entry.get("univentionObjectType", [])
            if not isinstance(object_types, list) or len(object_types) < 1:
                MODULE.warn("ReadControl response is missing `univentionObjectType`!")
                return None

            try:
                object_type = object_types[0].decode("utf-8")
                module = self._get_module(object_type)
                module_obj = module.module.object(
                    co=None,
                    lo=self,
                    position=None,
                    dn=entry["entryDN"][0],
                    superordinate=None,
                    attributes=entry,
                )
                module_obj.open()
                return Object.get_representation(module, module_obj, ["*"], self, False)
            except ModuleNotFound:
                MODULE.error(
                    "ReadControl response has object type %r, but the module was not found!"
                    % object_type
                )
                return None

        new = _ldap_to_udm(obj)

        # new = await self.resolve_references(new)
        old = await self.retrieve(
            new.get("entryDN")
        )  # FIXME: find the way to retrieve old object without new (by UUID)
        await self.store(new)

        if old:
            MODULE.debug("UDM before change")
            for key, value in sorted(old.items(), key=lambda i: i[0]):
                MODULE.debug(f"  {key}: {value}")
        if new:
            MODULE.debug("UDM after change")
            for key, value in sorted(new.items(), key=lambda i: i[0]):
                MODULE.debug(f"  {key}: {value}")

        await self.send_event(new, old)

    def _extract_responses(self, func, response_name, *args, **kwargs):
        pass

    async def add(self, dn, obj):
        await self._handle_control_responses(obj)

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
