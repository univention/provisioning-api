import json
import logging
from datetime import datetime
from typing import Optional

from shared.models import Message
from udm_messaging.port import UDMMessagingPort
from univention.admin.mapping import mapping, ListToString, mapDict

logger = logging.getLogger(__name__)


# FIXME: find a way to import this function from UCS
def mapTranslationValue(vals, encoding=()):
    return [" ".join(val).encode(*encoding) for val in vals]


# FIXME: find a way to import this function from UCS
def unmapTranslationValue(vals, encoding=()):
    return [val.decode(*encoding).split(" ", 1) for val in vals]


def register_mapping(map: mapping):
    map.register("name", "cn", None, ListToString)
    map.register(
        "needsConfirmation",
        "univentionNewPortalAnnouncementNeedsConfirmation",
        None,
        ListToString,
    )
    map.register(
        "isSticky", "univentionNewPortalAnnouncementIsSticky", None, ListToString
    )
    map.register(
        "severity", "univentionNewPortalAnnouncementSeverity", None, ListToString
    )
    map.register(
        "title",
        "univentionNewPortalAnnouncementTitle",
        mapTranslationValue,
        unmapTranslationValue,
    )
    # objectClass??
    # univentionObjectType??
    # structuralObjectClass??
    # entryUUID??
    # creatorsName??
    # createTimestamp??
    # modifiersName??
    # modifyTimestamp??
    # entryDN??
    # subschemaSubentry??
    # hasSubordinates??


MAP = mapping()
register_mapping(MAP)


class UDMMessagingService:
    def __init__(self, port: UDMMessagingPort):
        self._port = port

    async def retrieve(self, url: str):
        return await self._port.retrieve(url)

    async def store(self, new_obj: dict):
        await self._port.store(new_obj["entryUUID"][0].decode(), json.dumps(new_obj))

    async def send_event(self, new_obj: Optional[dict], old_obj: Optional[dict]):
        object_type = "users/user"  # FIXME: this value is mocked. Need to find correct reference

        message = Message(
            publisher_name="udm-listener",
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={"old": old_obj, "new": new_obj},
        )
        await self._port.send_event(message)

    async def resolve_references(self, obj: dict):
        fields_to_resolve = ("creatorsName", "modifiersName")
        for field in fields_to_resolve:
            value = obj[field]
            resolved_value = await self._port.get_object(f"users/user/{value}")
            obj[field] = resolved_value
        return obj

    async def handle_changes(self, new_obj: Optional[dict], old_obj: Optional[dict]):
        if not new_obj:
            old_obj = await self.retrieve(old_obj["entryUUID"][0].decode())
        else:
            old_obj = await self.retrieve(new_obj["entryUUID"][0].decode())
            new_obj = mapDict(MAP, new_obj)  # convert ldap obj to udm obj
            new_obj = await self.resolve_references(new_obj)
            await self.store(new_obj)
        await self.send_event(new_obj, old_obj)
