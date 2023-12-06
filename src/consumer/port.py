import contextlib
from typing import List, Annotated, Optional

from fastapi import Depends

from shared.adapters.nats_adapter import NatsAdapter, NatsKeys
from shared.adapters.nats_kv_adapter import NatsKVAdapter
from shared.adapters.message_queue import MessageQueueAdapter
from shared.adapters.kv_store import KVStoreAdapter

from shared.config import settings
from shared.models import Message
from shared.models.queue import MQMessage


class ConsumerPort:
    def __init__(self):
        self.message_queue = MessageQueueAdapter(message_queue=NatsAdapter())
        self.kv_store = KVStoreAdapter(kv_store=NatsKVAdapter())

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = ConsumerPort()
        await port.message_queue.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port.kv_store.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )

        await port.kv_store.create_kv_store()
        try:
            yield port
        finally:
            await port.close()

    @staticmethod
    async def port_dependency():
        port = ConsumerPort()
        await port.message_queue.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port.kv_store.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )

        await port.kv_store.create_kv_store()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.message_queue.close()
        await self.kv_store.close()

    async def add_live_message(self, subscriber_name: str, message: Message):
        await self.message_queue.add_message(subscriber_name, message)

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        await self.kv_store.add_prefill_message(subscriber_name, message)

    async def delete_prefill_messages(self, subscriber_name: str):
        await self.kv_store.delete_prefill_messages(subscriber_name)

    async def get_next_message(
        self, subscriber_name: str, timeout: float, pop: bool
    ) -> List[MQMessage]:
        return await self.message_queue.get_messages(subscriber_name, timeout, 1, pop)

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        return await self.message_queue.get_messages(
            subscriber_name, timeout, count, pop
        )

    async def remove_message(self, msg: MQMessage):
        await self.message_queue.remove_message(msg)

    async def delete_queue(self, subscriber_name: str):
        await self.message_queue.delete_stream(subscriber_name)

    async def get_subscriber_names(self) -> List[str]:
        return await self.kv_store.get_subscribers_for_key(NatsKeys.subscribers)

    async def get_subscriber_info(self, name: str) -> Optional[dict]:
        return await self.kv_store.get_subscriber_info(name)

    async def add_subscriber(
        self,
        name: str,
        realm_topic: str,
        fill_queue: bool,
        fill_queue_status: str,
    ):
        await self.kv_store.add_subscriber(
            name, realm_topic, fill_queue, fill_queue_status
        )

    async def create_subscription(self, name: str, realm_topic: str, sub_info: dict):
        await self.kv_store.create_subscription(name, realm_topic, sub_info)

    async def set_subscriber_queue_status(self, name: str, sub_info: dict) -> None:
        return await self.kv_store.set_subscriber_queue_status(name, sub_info)

    async def delete_subscriber(self, name: str):
        await self.kv_store.delete_subscriber(name)

    async def get_subscribers_for_topic(self, realm_topic: str) -> List[str]:
        return await self.kv_store.get_subscribers_for_key(realm_topic)

    async def update_sub_info(self, name, sub_info: dict):
        await self.kv_store.put_value_by_key(NatsKeys.subscriber(name), sub_info)


ConsumerPortDependency = Annotated[ConsumerPort, Depends(ConsumerPort.port_dependency)]
