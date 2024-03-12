# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from typing import Optional

from udm_messaging.config import udm_producer_settings
from shared.models.subscription import Bucket
from shared.models import Message, PublisherName
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
            host=udm_producer_settings.ldap_host,
            port=udm_producer_settings.ldap_port,
            start_tls=2 if udm_producer_settings.tls_mode.lower() == "on" else 0,
            base=udm_producer_settings.ldap_base_dn,
            binddn=udm_producer_settings.ldap_host_dn,
            bindpw=udm_producer_settings.ldap_password,
        )
        self._messaging_port = port
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def retrieve(self, dn: str):
        self.logger.info("Retrieving object from cache")
        return await self._messaging_port.retrieve(dn, Bucket.cache)

    async def store(self, new_obj: dict):
        self.logger.info("Storing object to cache %s", new_obj)
        await self._messaging_port.store(
            new_obj["uuid"], json.dumps(new_obj), Bucket.cache
        )

    async def send_event(self, new_obj: Optional[dict], old_obj: Optional[dict]):
        if not (new_obj or old_obj):
            return

        object_type = (
            new_obj.get("objectType") if new_obj else old_obj.get("objectType")
        )

        if not object_type:
            self.logger.error(
                "could not identify objectType", {"old": old_obj, "new": new_obj}
            )
            return

        message = Message(
            publisher_name=PublisherName.udm_listener,
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={"new": new_obj, "old": old_obj},
        )
        self.logger.info("Sending event with body: %s", message.body)
        await self._messaging_port.send_event(message)

    def _get_module(self, object_type):
        module = UDM_Module(object_type, ldap_connection=self, ldap_position=None)
        if not module or not module.module:
            raise ModuleNotFound
        return module

    def ldap_to_udm(self, entry: dict) -> Optional[dict]:
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

    async def handle_changes(self, new_obj, old_obj):
        old = (
            await self.retrieve(old_obj["entryUUID"][0].decode())
            if old_obj
            else old_obj
        )
        new = None
        if new_obj:
            new = self.ldap_to_udm(new_obj)
            if new:
                await self.store(new)
        await self.send_event(new, old or old_obj)


class ModuleNotFound(Exception):
    pass
