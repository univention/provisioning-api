# Callable | NoneSPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import importlib
import json
import logging
from datetime import datetime

import univention.admin.uldap
from udm_transformer.port import UDMTransformerPort
from univention.admin.rest.module import Object
from univention.management.console.log import MODULE
from univention.management.console.modules.udm.udm_ldap import UDM_Module
from univention.provisioning.models import Bucket, Message
from univention.provisioning.models.queue import Body

logger = logging.getLogger(__name__)

SUPPORTED_OBJECT_TYPES = [
    "oxmail/accessprofile",
    "oxmail/functional_account",
    "oxmail/oxcontext",
    "oxresources/oxresources",
    "portals/all",
    "portals/announcement",
    "portals/category",
    "portals/entry",
    "portals/folder",
    "portals/portal",
    "portals/announcement",
    "portals/category",
    "portals/entry",
    "portals/folder",
    "portals/portal",
    "users/user",
    "groups/group",
]

UDM_MODULES_RELOAD_TRIGGER = {
    "settings/extended_attribute",
    "settings/extended_options",
    "settings/udm_hook",
    "settings/udm_module",
    "settings/udm_syntax",
}


class UDMMessagingService(univention.admin.uldap.access):
    def __init__(self, port: UDMTransformerPort):
        super().__init__(
            host=port.settings.ldap_host,
            port=port.settings.ldap_port,
            start_tls=2 if port.settings.ldap_tls_mode.lower() == "on" else 0,
            base=port.settings.ldap_base_dn,
            binddn=port.settings.ldap_bind_dn,
            bindpw=port.settings.ldap_bind_pw,
        )
        self._my_ldap_position = univention.admin.uldap.position(port.settings.ldap_base_dn)
        self.ldap_publisher_name = port.settings.ldap_publisher_name

        self._messaging_port = port

    @staticmethod
    def reload_udm(obj: dict):
        if obj.get("objectType") not in UDM_MODULES_RELOAD_TRIGGER:
            return

        logger.info("Reload of UDM modules triggered after creating/updating/deleting %r object.", obj["objectType"])
        importlib.reload(univention.management.console.modules.udm.udm_ldap)

    async def retrieve(self, dn: str) -> dict:
        logger.debug("Retrieving object from cache")
        return await self._messaging_port.retrieve(dn, Bucket.cache)

    async def store(self, new_obj: dict):
        logger.debug("Storing object to cache with dn: %r", new_obj.get("dn"))
        await self._messaging_port.store(new_obj["uuid"], json.dumps(new_obj), Bucket.cache)

    async def send_event(self, new_obj: dict, old_obj: dict, ts: datetime):
        if not (new_obj or old_obj):
            return

        object_type = new_obj.get("objectType") if new_obj else old_obj.get("objectType")

        if not object_type:
            logger.error("could not identify objectType for dn: %r", new_obj.get("dn") or old_obj.get("dn"))
            logger.debug("old_obj: %r, new_obj: %r", old_obj, new_obj)
            return

        message = Message(
            publisher_name=self.ldap_publisher_name,
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body=Body(old=old_obj, new=new_obj),
        )
        logger.debug("Sending the message with body: %r", message.body)
        await self._messaging_port.send_event(message)
        logger.info("The message was sent")

    def _get_module(self, object_type):
        module = UDM_Module(object_type, ldap_connection=self, ldap_position=self._my_ldap_position)
        if not module or not module.module:
            raise ModuleNotFound
        return module

    def ldap_to_udm(self, entry: dict) -> dict:
        object_types = entry.get("univentionObjectType", [])
        if not isinstance(object_types, list) or len(object_types) < 1:
            MODULE.warn("ReadControl response is missing `univentionObjectType`!")
            return {}

        object_type = object_types[0].decode("utf-8")
        try:
            module = self._get_module(object_type)
            module_obj = module.module.object(
                co=None,
                lo=self,
                position=self._my_ldap_position,
                dn=entry["entryDN"][0],
                superordinate=None,
                attributes=entry,
            )
            module_obj.open()
            return Object.get_representation(module, module_obj, ["*"], self, False)
        except ModuleNotFound:
            MODULE.error("ReadControl response has object type %r, but the module was not found!" % object_type)
            return {}
        except Exception:
            if object_type in SUPPORTED_OBJECT_TYPES:
                raise
            logger.exception(
                "Ignoring the failed transformation of a udm type: %r "
                "because it's not a supported provisioning topic\n"
                "object: %r",
                object_type,
                entry,
            )

    async def handle_changes(self, new_obj, old_obj, ts: datetime):
        old = {}
        if old_obj:
            old = await self.retrieve(old_obj["entryUUID"][0].decode())
        new = {}
        if new_obj:
            new = self.ldap_to_udm(new_obj)
            if new:
                await self.store(new)

        self.reload_udm(new or old)
        await self.send_event(new, old, ts)


class ModuleNotFound(Exception):
    pass
