from typing import List, Tuple, Optional, cast, Dict

from redis.asyncio import Redis

from core.models import Message


class RedisKeys:
    """A list of keys used in Redis for queueing messages and storing subscriptions."""

    subscribers = "subscribers"

    def queue(subscriber_name):
        return f"queue:{subscriber_name}"

    def subscriber(subscriber_name: str) -> str:
        return f"subscriber:{subscriber_name}"

    def subscriber_topics(subscriber_name: str) -> str:
        return f"subscriber_topics:{subscriber_name}"


class RedisAdapter:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def add_live_message(self, subscriber_name: str, message: Message):
        flat_message = message.flatten()
        await self.redis.xadd(RedisKeys.queue(subscriber_name), flat_message, "*")

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        flat_message = message.flatten()
        await self.redis.xadd(RedisKeys.queue(subscriber_name), flat_message, "0-*")

    async def delete_prefill_messages(self, subscriber_name: str):
        await self.redis.xtrim(RedisKeys.queue(subscriber_name), minid=1)

    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[Tuple[str, Message]]:
        key = RedisKeys.queue(subscriber_name)

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
        response = await self.redis.xrange(
            RedisKeys.queue(subscriber_name), first, last, count
        )

        return [
            (message_id, Message.inflate(flat_message))
            for message_id, flat_message in response
        ]

    async def delete_message(self, subscriber_name: str, message_id: str):
        await self.redis.xdel(RedisKeys.queue(subscriber_name), message_id)

    async def delete_queue(self, subscriber_name: str):
        await self.redis.xtrim(RedisKeys.queue(subscriber_name), maxlen=0)

    async def get_subscriber_names(self) -> List[str]:
        return await self.redis.smembers(RedisKeys.subscribers)

    async def get_subscriber_by_name(self, name: str):
        return await self.redis.sismember(RedisKeys.subscribers, name)

    async def get_subscriber_info(self, name: str):
        return await self.redis.hgetall(RedisKeys.subscriber(name))

    async def get_subscriber_topics(self, name: str):
        return await self.redis.smembers(RedisKeys.subscriber_topics(name))

    async def add_subscriber(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        fill_queue: bool,
        fill_queue_status: str,
    ):
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.sadd(RedisKeys.subscribers, name)
            pipe.hset(
                RedisKeys.subscriber(name),
                mapping={
                    "name": name,
                    "fill_queue": int(fill_queue),
                    "fill_queue_status": fill_queue_status,
                },
            )

            for realm, topic in realms_topics:
                pipe.sadd(RedisKeys.subscriber_topics(name), f"{realm}:{topic}")

            await pipe.execute()

    async def get_subscriber_queue_status(self, name: str):
        return await self.redis.hget(RedisKeys.subscriber(name), "fill_queue_status")

    async def set_subscriber_queue_status(self, name: str, status: str):
        return await self.redis.hset(
            RedisKeys.subscriber(name), "fill_queue_status", status
        )

    async def delete_subscriber(self, name: str):
        async with self.redis.pipeline(transaction=True) as pipe:
            pipe.delete(RedisKeys.subscriber_topics(name))
            pipe.delete(RedisKeys.subscriber(name))
            pipe.srem(RedisKeys.subscribers, name)
            await pipe.execute()
