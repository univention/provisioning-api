import contextlib
from typing import List, Annotated, Optional

from fastapi import Depends

from shared.adapters.nats_adapter import NatsAdapter, NatsKeys
from shared.adapters.redis_adapter import RedisAdapter
from shared.config import settings
from shared.models import Message

from shared.models.queue import NatsMessage


class ConsumerPort:
    def __init__(self):
        self.redis_adapter = RedisAdapter()
        self.nats_adapter = NatsAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = ConsumerPort()
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
        port = ConsumerPort()
        await port.nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port.nats_adapter.create_kv_store()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.redis_adapter.close()
        await self.nats_adapter.close()

    async def add_live_message(self, subscriber_name: str, message: Message):
        await self.nats_adapter.add_message(subscriber_name, message)

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        await self.redis_adapter.add_prefill_message(subscriber_name, message)

    async def delete_prefill_messages(self, subscriber_name: str):
        await self.redis_adapter.delete_prefill_messages(subscriber_name)

    async def get_next_message(
        self, subscriber_name: str, timeout: float, pop: bool
    ) -> List[NatsMessage]:
        return await self.nats_adapter.get_messages(subscriber_name, timeout, 1, pop)

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        return await self.nats_adapter.get_messages(
            subscriber_name, timeout, count, pop
        )

    async def remove_message(self, msg: NatsMessage):
        await self.nats_adapter.remove_message(msg)

    async def delete_queue(self, subscriber_name: str):
        await self.nats_adapter.delete_stream(subscriber_name)

    async def get_subscriber_names(self) -> List[str]:
        return await self.nats_adapter.get_subscribers_for_key(NatsKeys.subscribers)

    async def get_subscriber_info(self, name: str) -> Optional[dict]:
        return await self.nats_adapter.get_subscriber_info(name)

    async def add_subscriber(
        self,
        name: str,
        realm_topic: str,
        fill_queue: bool,
        fill_queue_status: str,
    ):
        await self.nats_adapter.add_subscriber(
            name, realm_topic, fill_queue, fill_queue_status
        )

    async def create_subscription(self, name: str, realm_topic: str, sub_info: dict):
        await self.nats_adapter.create_subscription(name, realm_topic, sub_info)

    async def set_subscriber_queue_status(self, name: str, sub_info: dict) -> None:
        return await self.nats_adapter.set_subscriber_queue_status(name, sub_info)

    async def delete_subscriber(self, name: str):
        await self.nats_adapter.delete_subscriber(name)

    async def get_subscribers_for_topic(self, realm_topic: str) -> List[str]:
        return await self.nats_adapter.get_subscribers_for_key(realm_topic)

    async def update_sub_info(self, name, sub_info: dict):
        await self.nats_adapter.put_value_by_key(NatsKeys.subscriber(name), sub_info)


ConsumerPortDependency = Annotated[ConsumerPort, Depends(ConsumerPort.port_dependency)]
