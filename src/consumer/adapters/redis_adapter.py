from redis.asyncio import Redis

from core.models import Message


class Keys:
    """A list of keys used in Redis for queueing messages."""

    def queue(subscriber_name):
        return f"queue:{subscriber_name}"


class RedisAdapter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_live_message(self, subscriber_name: str, message: Message):
        key = Keys.queue(subscriber_name)
        flat_message = message.flatten()
        await self.redis.xadd(key, flat_message, "*")
