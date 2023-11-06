from redis.asyncio import Redis

from consumer.adapters.redis_adapter import RedisAdapter
from core.models import Message


class Port:
    def __init__(self, redis: Redis):
        self.redis_adapter = RedisAdapter(redis)

    async def add_live_message(self, subscriber_name: str, message: Message):
        await self.redis_adapter.add_live_message(subscriber_name, message)
