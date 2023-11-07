from typing import Annotated, Any, Dict, List, Optional, Tuple

import fastapi
from redis.asyncio import Redis

from consumer.core.persistence.redis import RedisDependency
from consumer.port import Port


class Keys:
    """
    A list of keys used in Redis for storing subscriptions.
    """

    subscribers = "subscribers"

    def subscriber(subscriber_name: str) -> str:
        return f"subscriber:{subscriber_name}"

    def subscriber_topics(subscriber_name: str) -> str:
        return f"subscriber_topics:{subscriber_name}"


class SubscriptionRepositoryRedis:
    """
    Store and retrieve subscription information from Redis.
    """

    def __init__(self, redis: Redis):
        self.redis = redis
        self.port = Port(redis)

    async def get_subscriber_names(self) -> List[str]:
        """
        Return a list of names of all known subscribers.
        """

        return await self.port.get_subscriber_names()

    async def get_subscriber(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a registered subscriber.
        """

        if not await self.port.get_subscriber_by_name(name):
            raise ValueError("Subscriber not found.")

        sub = await self.port.get_subscriber_info(name)
        sub_topics = await self.port.get_subscriber_topics(name)
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
            realms_topics = await self.port.get_subscriber_topics(name)
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

        if await self.port.get_subscriber_by_name(name):
            raise ValueError("Subscriber already exists.")

        await self.port.add_subscriber(
            name, realms_topics, fill_queue, fill_queue_status
        )

    async def get_subscriber_queue_status(self, name: str) -> str:
        """
        Get the pre-fill status of the subscriber.
        """

        if not await self.port.get_subscriber_by_name(name):
            raise ValueError("Subscriber not found.")

        return await self.port.get_subscriber_queue_status(name)

    async def set_subscriber_queue_status(self, name: str, status: str):
        """
        Set the pre-fill status of the subscriber.
        """

        if not await self.port.get_subscriber_by_name(name):
            raise ValueError("Subscriber not found.")

        await self.port.set_subscriber_queue_status(name, status)

    async def delete_subscriber(self, name: str):
        """
        Delete a subscriber and all of its data.
        """

        if not await self.port.get_subscriber_by_name(name):
            raise ValueError("Subscriber not found.")

        await self.port.delete_subscriber(name)


class SubscriptionRepository(SubscriptionRepositoryRedis):
    def __init__(self, redis: redis.Redis | None):
        # TODO: implement SubscriptionRepositoryPostgres
        # TODO: choose proper implementation based on the __init__ call signature
        if not redis:
            raise NotImplementedError(
                "SubscriptionRepository currently requires a Redis dependency"
            )
        SubscriptionRepositoryRedis.__init__(self, redis=redis)


def get_subscription_repository(redis: RedisDependency) -> SubscriptionRepository:
    return SubscriptionRepository(redis)


DependsSubscriptionRepo = Annotated[
    SubscriptionRepository, fastapi.Depends(get_subscription_repository)
]
