from typing import List, Tuple, Optional

from core.models import Message
from core.models.adapters import BaseKVStore

class KVStoreAdapter:
    def __init__(self, kv_store: BaseKVStore):
        self.kv_store = kv_store

    async def add_live_message(self, subscriber_name: str, message: Message):
        return await self.kv_store.add_live_message(
            subscriber_name=subscriber_name, message=message
        )

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        """TODO: Add a message to the prefill queue."""
        return await self.kv_store.add_prefill_message(
            subscriber_name=subscriber_name, message=message
        )

    async def delete_prefill_messages(self, subscriber_name: str):
        """TODO: Remove a message from the prefill queue."""
        return await self.kv_store.delete_prefill_message(
            subscriber_name=subscriber_name
        )

    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[List[Tuple[str, Message]]]:
        return await self.kv_store.get_next_message(
            subscriber_name=subscriber_name, block=block
        )

    async def get_messages(
        self,
        subscriber_name: str,
        count: Optional[int] = None,
        first: int | str = "-",
        last: int | str = "+",
    ):
        return await self.kv_store.get_messages(
            subscriber_name=subscriber_name, count=count, first=first, last=last
        )

    async def delete_message(self, subscriber_name: str, message_id: str):
        return await self.kv_store.delete_message(subscriber_name=subscriber_name)

    async def delete_queue(self, subscriber_name: str):
        return await self.kv_store.delete_queue(subscriber_name=subscriber_name)

    async def get_subscriber_names(self):
        return await self.kv_store.get_subscriber_names()

    async def get_subscriber_by_name(self, name: str):
        return await self.kv_store.get_subscriber_by_name(name=name)

    async def get_subscriber_info(self, name: str):
        return await self.kv_store.get_subscriber_info(name=name)

    async def get_subscriber_topics(self, name: str):
        return await self.kv_store.get_subscriber_topics(name=name)

    async def add_subscriber(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        fill_queue: bool,
        fill_queue_status: str,
    ):
        return await self.kv_store.add_subscriber(
            name=name,
            realms_topics=realms_topics,
            fill_queue=fill_queue,
            fill_queue_status=fill_queue_status,
        )

    async def get_subscriber_queue_status(self, name: str):
        return await self.kv_store.get_subscriber_queue_status(name=name)

    async def set_subscriber_queue_status(self, name: str, status: str):
        return await self.kv_store.set_subscriber_queue_status(name=name, status=status)

    async def delete_subscriber(self, name: str):
        return await self.kv_store.delete_subscriber(name=name)
