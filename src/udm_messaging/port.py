import contextlib
from typing import Optional

from shared.adapters.nats_adapter import NatsAdapter
from shared.adapters.notification_adapter import NotificationAdapter

from shared.config import settings
from shared.models import Message


class UDMMessagingPort:
    def __init__(self):
        self._nats_adapter = NatsAdapter()
        self._notification_adapter: Optional[NotificationAdapter] = None

    async def init_notification_adapter(self):
        async with NotificationAdapter(
            settings.notif_url, settings.notif_username, settings.notif_password
        ) as adapter:
            self._notification_adapter = adapter

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMMessagingPort()
        await port.init_notification_adapter()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()
        yield port

    async def retrieve(self, url: str):
        return await self._nats_adapter.get_value_by_key(url)

    async def store(self, url: str, new_obj: str):
        await self._nats_adapter.put_value_by_key(url, new_obj)

    async def send_notification(self, message: Message):
        await self._notification_adapter.send_notification(message)
