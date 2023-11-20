import contextlib
from typing import Annotated

from fastapi import Depends

from shared.adapters.nats_adapter import NatsAdapter
from shared.config import settings
from shared.models import Message


class EventsPort:
    def __init__(self):
        self.nats_adapter = NatsAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = EventsPort()
        await port.nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port.nats_adapter.create_kv_store()
        try:
            yield port
        finally:
            await port.close()

    @staticmethod
    async def port_dependency():
        port = EventsPort()
        await port.nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port.nats_adapter.create_kv_store()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.nats_adapter.close()

    async def add_live_message(self, message: Message):
        # TODO: define the name "incoming" globally or handle it differently alltogether
        await self.nats_adapter.add_message("incoming", message)


EventsPortDependency = Annotated[EventsPort, Depends(EventsPort.port_dependency)]
