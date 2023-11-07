from typing import Optional, Tuple, List

from redis.asyncio import Redis

from consumer.adapters.redis_adapter import RedisAdapter
from core.models import Message


class Port:
    def __init__(self, redis: Redis):
        self.redis_adapter = RedisAdapter(redis)

    async def add_live_message(self, subscriber_name: str, message: Message):
        await self.redis_adapter.add_live_message(subscriber_name, message)

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        await self.redis_adapter.add_prefill_message(subscriber_name, message)

    async def delete_prefill_messages(self, subscriber_name: str):
        await self.redis_adapter.delete_prefill_messages(subscriber_name)

    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[Tuple[str, Message]]:
        return await self.redis_adapter.get_next_message(subscriber_name, block)

    async def get_messages(
        self,
        subscriber_name: str,
        count: Optional[int] = None,
        first: int | str = "-",
        last: int | str = "+",
    ):
        return await self.redis_adapter.get_messages(
            subscriber_name, count, first, last
        )

    async def delete_message(self, subscriber_name: str, message_id: str):
        await self.redis_adapter.delete_message(subscriber_name, message_id)

    async def delete_queue(self, subscriber_name: str):
        await self.redis_adapter.delete_queue(subscriber_name)

    async def get_subscriber_names(self) -> List[str]:
        return await self.redis_adapter.get_subscriber_names()

    async def get_subscriber_by_name(self, name: str):
        return await self.redis_adapter.get_subscriber_by_name(name)

    async def get_subscriber_info(self, name: str):
        return await self.redis_adapter.get_subscriber_info(name)

    async def get_subscriber_topics(self, name: str):
        return await self.redis_adapter.get_subscriber_topics(name)

    async def add_subscriber(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        fill_queue: bool,
        fill_queue_status: str,
    ):
        await self.redis_adapter.add_subscriber(
            name, realms_topics, fill_queue, fill_queue_status
        )

    async def get_subscriber_queue_status(self, name: str):
        return await self.redis_adapter.get_subscriber_queue_status(name)

    async def set_subscriber_queue_status(self, name: str, status: str):
        return await self.redis_adapter.set_subscriber_queue_status(name, status)

    async def delete_subscriber(self, name: str):
        await self.redis_adapter.delete_subscriber(name)
