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
    ) -> List[Tuple[str, Message]]:
        return await self.redis_adapter.get_messages(
            subscriber_name, count, first, last
        )

    async def delete_message(self, subscriber_name: str, message_id: str):
        await self.redis_adapter.delete_message(subscriber_name, message_id)

    async def delete_queue(self, subscriber_name: str):
        await self.redis_adapter.delete_queue(subscriber_name)
