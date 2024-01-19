# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Tuple, Optional

from redis.asyncio import Redis

from shared.config import settings
from shared.models import Message

logger = logging.getLogger(__name__)


class RedisKeys:
    """A list of keys used in Redis for queueing messages and storing subscriptions."""

    subscribers = "subscribers"

    def queue(subscriber_name: str) -> str:
        return f"queue:{subscriber_name}"

    def subscriber(subscriber_name: str) -> str:
        return f"subscriber:{subscriber_name}"

    def subscriber_topics(subscriber_name: str) -> str:
        return f"subscriber_topics:{subscriber_name}"


class RedisAdapter:
    def __init__(self, redis: Redis = None):
        self.redis = (
            redis
            if redis
            else Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                decode_responses=True,
                protocol=3,
            )
        )

    async def close(self):
        await self.redis.close()

    async def add_live_message(self, subscriber_name: str, message: Message):
        flat_message = message.model_dump()
        await self.redis.xadd(RedisKeys.queue(subscriber_name), flat_message, "*")

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        flat_message = message.model_dump()
        await self.redis.xadd(RedisKeys.queue(subscriber_name), flat_message, "0-*")

    async def delete_prefill_messages(self, subscriber_name: str):
        await self.redis.xtrim(RedisKeys.queue(subscriber_name), minid=1)

    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[List[Tuple[str, Message]]]:
        return await self.redis.xread(
            {RedisKeys.queue(subscriber_name): "0-0"}, count=1, block=block
        )

    async def get_messages(
        self,
        subscriber_name: str,
        count: Optional[int] = None,
        first: int | str = "-",
        last: int | str = "+",
    ):
        response = await self.redis.xrange(
            RedisKeys.queue(subscriber_name), first, last, count
        )
        return [
            (message_id, Message.model_validate(flat_message))
            for message_id, flat_message in response
        ]

    async def delete_message(self, subscriber_name: str, message_id: str):
        await self.redis.xdel(RedisKeys.queue(subscriber_name), message_id)

    async def delete_queue(self, subscriber_name: str):
        await self.redis.xtrim(RedisKeys.queue(subscriber_name), maxlen=0)

    async def get_subscriber_names(self):
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
        request_prefill: bool,
        prefill_queue_status: str,
    ):
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.sadd(RedisKeys.subscribers, name)
            await pipe.hset(
                RedisKeys.subscriber(name),
                mapping={
                    "name": name,
                    "request_prefill": int(request_prefill),
                    "prefill_queue_status": prefill_queue_status,
                },
            )

            for realm, topic in realms_topics:
                await pipe.sadd(RedisKeys.subscriber_topics(name), f"{realm}:{topic}")

            await pipe.execute()

    async def get_subscriber_queue_status(self, name: str):
        return await self.redis.hget(RedisKeys.subscriber(name), "prefill_queue_status")

    async def set_subscriber_queue_status(self, name: str, status: str):
        await self.redis.hset(
            RedisKeys.subscriber(name), "prefill_queue_status", status
        )

    async def delete_subscriber(self, name: str):
        async with self.redis.pipeline(transaction=True) as pipe:
            await pipe.delete(RedisKeys.subscriber_topics(name))
            await pipe.delete(RedisKeys.subscriber(name))
            await pipe.srem(RedisKeys.subscribers, name)
            await pipe.execute()
