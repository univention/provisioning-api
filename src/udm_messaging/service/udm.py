import logging
from datetime import datetime

from shared.models import Message
from udm_messaging.port import UDMMessagingPort

logger = logging.getLogger(__name__)


class UDMMessagingService:
    def __init__(self, port: UDMMessagingPort):
        self._port = port

    async def get_new_object(self, url: str):
        return await self._port.get_new_object(url)

    async def retrieve_old_obj(self):
        return await self._port.retrieve_old_obj()

    def store_old_obj(self):
        self._port.store_old_obj()

    async def send_notification(self, url: str, object_type: str):
        new_obj = await self.get_new_object(url)
        old_obj = await self.retrieve_old_obj()

        message = Message(
            publisher_name="udm-pre-fill",
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={
                "old": old_obj,
                "new": new_obj,
            },
        )
        logger.info(f"Sending to queue from: {url}")
        await self._port.send_notification(message)

    async def handle_changes(self):
        pass
