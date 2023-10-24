from typing import Annotated, Any, Dict, List, Optional, Tuple

import fastapi
import redis.asyncio as redis

from consumer.core.persistence.redis import RedisDependency


class Keys:
    """
    A list of keys used in Redis for storing subscriptions.
    """

    subscribers = "subscribers"

    def subscriber(subscriber_name: str) -> str:
        return f"subscriber:{subscriber_name}"

    def subscriber_topics(subscriber_name: str) -> str:
        return f"subscriber_topics:{subscriber_name}"


class SubscriptionRepository:
    """
    Store and retrieve subscription information from Redis.
    """

    def __init__(self, redis: redis.Redis):
        self._redis = redis

    async def get_subscriber_names(self) -> List[str]:
        """
        Return a list of names of all known subscribers.
        """

        subs = await self._redis.smembers(Keys.subscribers)
        return subs

    async def get_subscriber(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered subscriber.
        """

        if not await self._redis.sismember(Keys.subscribers, name):
            raise ValueError("Subscriber not found.")

        sub = await self._redis.hgetall(Keys.subscriber(name))
        sub_topics = await self._redis.smembers(Keys.subscriber_topics(name))
        realms_topics = [realm_topic.split(":", 1) for realm_topic in sub_topics]

        return dict(
            name=sub["name"],
            realms_topics=realms_topics,
            fill_queue=bool(int(sub["fill_queue"])),
            fill_queue_status=sub["fill_queue_status"],
        )

    async def get_subscribers_by_topics(self) -> List[Tuple[str, str, str]]:
        """
        Return a list of realm, topic and subscriber name for all subscriptions.
        """

        names = await self.get_subscriber_names()

        result = []

        for name in names:
            key = Keys.subscriber_topics(name)
            realms_topics = await self._redis.smembers(key)
            for realm_topic in realms_topics:
                realm, topic = realm_topic.split(":", 1)
                result.append((realm, topic, name))

        return result

    async def add_subscriber(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        fill_queue: bool,
        fill_queue_status: str,
    ):
        """
        Add a new subscriber.
        """

        if await self._redis.sismember(Keys.subscribers, name):
            raise ValueError("Subscriber already exists.")

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.sadd(Keys.subscribers, name)
            pipe.hset(
                Keys.subscriber(name),
                mapping={
                    "name": name,
                    "fill_queue": int(fill_queue),
                    "fill_queue_status": fill_queue_status,
                },
            )

            for realm, topic in realms_topics:
                pipe.sadd(Keys.subscriber_topics(name), f"{realm}:{topic}")

            await pipe.execute()

    async def get_subscriber_queue_status(self, name: str) -> str:
        """
        Get the pre-fill status of the subscriber.
        """

        if not await self._redis.sismember(Keys.subscribers, name):
            raise ValueError("Subscriber not found.")

        key = Keys.subscriber(name)
        return await self._redis.hget(key, "fill_queue_status")

    async def set_subscriber_queue_status(self, name: str, status: str):
        """
        Set the pre-fill status of the subscriber.
        """

        if not await self._redis.sismember(Keys.subscribers, name):
            raise ValueError("Subscriber not found.")

        key = Keys.subscriber(name)
        await self._redis.hset(key, "fill_queue_status", status)

    async def delete_subscriber(self, name: str):
        """
        Delete a subscriber and all of its data.
        """

        if not await self._redis.sismember(Keys.subscribers, name):
            raise ValueError("Subscriber not found.")

        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.delete(Keys.subscriber_topics(name))
            pipe.delete(Keys.subscriber(name))
            pipe.srem(Keys.subscribers, name)
            await pipe.execute()


def get_subscription_repository(redis: RedisDependency) -> SubscriptionRepository:
    return SubscriptionRepository(redis)


DependsSubscriptionRepo = Annotated[
    SubscriptionRepository, fastapi.Depends(get_subscription_repository)
]
