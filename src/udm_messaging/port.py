import contextlib
from typing import Optional

from shared.adapters.nats_adapter import NatsAdapter
from shared.adapters.event_adapter import EventAdapter

from shared.config import settings
from shared.models import Message


class UDMMessagingPort:
    def __init__(self):
        self._nats_adapter = NatsAdapter()
        self._event_adapter: Optional[EventAdapter] = None

    async def init_event_adapter(self):
        async with EventAdapter(
            settings.event_url, settings.event_username, settings.event_password
        ) as adapter:
            self._event_adapter = adapter

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMMessagingPort()
        await port.init_event_adapter()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()
        yield port

    async def retrieve(self, url: str):
        return await self._nats_adapter.get_value(url)

    async def store(self, url: str, new_obj: str):
        await self._nats_adapter.put_value(url, new_obj)

    async def send_event(self, message: Message):
        await self._event_adapter.send_event(message)
