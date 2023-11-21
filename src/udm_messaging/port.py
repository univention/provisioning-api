import contextlib
from typing import Optional

from shared.adapters.cache_db_adapter import CacheDbAdapter
from shared.adapters.notification_adapter import NotificationAdapter
from shared.adapters.udm_adapter import UDMAdapter

from shared.config import settings
from shared.models import Message


class UDMMessagingPort:
    def __init__(self):
        self._cache_db_adapter = CacheDbAdapter()
        self._notification_adapter: Optional[NotificationAdapter] = None
        self._udm_adapter: Optional[UDMAdapter] = None

    async def init_udm_adapters(self):
        async with UDMAdapter(
            settings.udm_url, settings.udm_username, settings.udm_password
        ) as adapter:
            self._udm_adapter = adapter

    async def init_notification_adapter(self):
        async with NotificationAdapter(
            settings.notif_url, settings.notif_username, settings.notif_password
        ) as adapter:
            self._notification_adapter = adapter

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMMessagingPort()
        await port.init_udm_adapters()
        await port.init_notification_adapter()
        yield port

    async def get_new_object(self, url: str):
        return await self._udm_adapter.get_object(url)

    async def retrieve_old_obj(self):
        return await self._cache_db_adapter.retrieve_old_obj()

    async def store_old_obj(self):
        await self._cache_db_adapter.store_old_obj()

    async def send_notification(self, message: Message):
        await self._notification_adapter.send_notification(message)
