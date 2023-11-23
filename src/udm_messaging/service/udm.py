import json
import logging
from datetime import datetime
from typing import Optional

from shared.models import Message
from udm_messaging.port import UDMMessagingPort

logger = logging.getLogger(__name__)


class UDMMessagingService:
    def __init__(self, port: UDMMessagingPort):
        self._port = port

    async def retrieve(self, url: str):
        return await self._port.retrieve(url)

    async def store(self, new_obj: dict):
        await self._port.store(new_obj["url"], json.dumps(new_obj))

    async def send_notification(self, new_obj: Optional[dict], old_obj: Optional[dict]):
        object_type = ""  # FIXME: find type

        message = Message(
            publisher_name="udm-listener",
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={"old": old_obj, "new": new_obj},
        )
        await self._port.send_notification(message)

    def resolve_references(self, obj: dict):
        pass

    async def handle_changes(self, new_obj: Optional[dict]):
        old_obj = await self.retrieve(new_obj["url"])
        if new_obj:
            new_obj = self.resolve_references(new_obj)
            await self.store(new_obj)
        await self.send_notification(new_obj, old_obj)
