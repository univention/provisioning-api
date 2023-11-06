from typing import Optional, Tuple, cast, Dict, List

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

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        key = Keys.queue(subscriber_name)
        flat_message = message.flatten()
        await self.redis.xadd(key, flat_message, "0-*")

    async def delete_prefill_messages(self, subscriber_name: str):
        key = Keys.queue(subscriber_name)
        await self.redis.xtrim(key, minid=1)

    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[Tuple[str, Message]]:
        key = Keys.queue(subscriber_name)

        response = await self.redis.xread({key: "0-0"}, count=1, block=block)

        if key not in response:
            # empty stream
            return None

        entries = response[key][0]
        if entries:
            message_id, flat_message = cast(Tuple[str, Dict[str, str]], entries[0])
            message = Message.inflate(flat_message)
            return (message_id, message)

    async def get_messages(
        self,
        subscriber_name: str,
        count: Optional[int] = None,
        first: int | str = "-",
        last: int | str = "+",
    ) -> List[Tuple[str, Message]]:
        key = Keys.queue(subscriber_name)

        response = await self.redis.xrange(key, first, last, count)

        return [
            (message_id, Message.inflate(flat_message))
            for message_id, flat_message in response
        ]

    async def delete_message(self, subscriber_name: str, message_id: str):
        key = Keys.queue(subscriber_name)
        await self.redis.xdel(key, message_id)

    async def delete_queue(self, subscriber_name: str):
        key = Keys.queue(subscriber_name)
        await self.redis.xtrim(key, maxlen=0)
