import contextlib
from typing import Optional

from shared.adapters.nats_adapter import NatsAdapter
from shared.adapters.event_adapter import EventAdapter
from shared.adapters.udm_adapter import UDMAdapter

from shared.config import settings
from shared.models import Message


class UDMMessagingPort:
    def __init__(self):
        self._nats_adapter = NatsAdapter()
        self._event_adapter: Optional[EventAdapter] = None
        self._udm_adapter: Optional[UDMAdapter] = None

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMMessagingPort()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()
        yield port

    async def retrieve(self, url: str):
        return await self._nats_adapter.get_value_by_key(url)

    async def store(self, url: str, new_obj: str):
        await self._nats_adapter.put_value_by_key(url, new_obj)

    async def send_event(self, message: Message):
        async with EventAdapter(
            settings.event_url, settings.event_username, settings.event_password
        ) as adapter:
            self._event_adapter = adapter
            await self._event_adapter.send_event(message)

    async def get_object(self, url: str) -> dict:
        return await self._udm_adapter.get_object(url)
