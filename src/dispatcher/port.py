import contextlib
import logging
from typing import List

from nats.aio.msg import Msg

from shared.adapters.nats_adapter import NatsAdapter
from shared.config import settings
from shared.models.queue import NatsMessage

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self):
        self._nats_adapter = NatsAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()
        yield port

    async def retrieve_event_from_queue(
        self, subject, timeout, pop
    ) -> List[NatsMessage]:
        return await self._nats_adapter.get_messages(subject, timeout, 1, pop)

    async def store_event_in_queue(self, subject: str, message):
        await self._nats_adapter.add_message(subject, message)

    async def get_list_value(self, key: str) -> List[str]:
        result = await self._nats_adapter.get_value(key)
        return result.value.decode("utf-8").split(",") if result else []

    async def subscribe_to_queue(self, subject: str):
        await self._nats_adapter.subscribe_to_queue(subject)

    async def wait_for_event(self) -> Msg:
        return await self._nats_adapter.wait_for_event()
