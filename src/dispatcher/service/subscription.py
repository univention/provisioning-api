import re
from typing import List

import core.models
from dispatcher.persistence.messages import MessageRepository
from dispatcher.persistence.subscriptions import SubscriptionRepository


def _match_subscription(
    sub_realm: str, sub_topic: str, msg_realm: str, msg_topic: str
) -> bool:
    """Decides whether a message is sent to a subscriber.

    Compares the subscriber's realm and topic to those of the message and
    returns `True` if the message should be sent to the subscriber.
    """

    if sub_realm != msg_realm:
        return False

    return re.fullmatch(sub_topic, msg_topic) is not None


class SubscriptionService:
    def __init__(self, repo: SubscriptionRepository):
        self._repo = repo

    async def get_subscribers(self) -> List[core.models.Subscriber]:
        """
        Return a list of names of all known subscribers.
        """

        names = await self._repo.get_subscriber_names()
        subscribers = [await self.get_subscriber(name) for name in names]
        return subscribers

    async def get_subscriber(self, name: str) -> core.models.Subscriber:
        """
        Get information about a registered subscriber.
        """

        data = await self._repo.get_subscriber(name)
        return core.models.Subscriber.model_validate(data)

    async def get_subscribers_for_topic(self, realm: str, topic: str) -> List[str]:
        """
        Return a list names of everyone subscribed to a given realm and topic.
        """

        return [
            s_name
            for s_realm, s_topic, s_name in await self._repo.get_subscribers_by_topics()
            if _match_subscription(s_realm, s_topic, realm, topic)
        ]

    async def add_subscriber(self, sub: core.models.NewSubscriber):
        """
        Add a new subscriber.
        """

        if sub.fill_queue:
            fill_queue_status = core.models.FillQueueStatus.pending
        else:
            fill_queue_status = core.models.FillQueueStatus.done

        await self._repo.add_subscriber(
            name=sub.name,
            realms_topics=sub.realms_topics,
            fill_queue=sub.fill_queue,
            fill_queue_status=fill_queue_status,
        )

    async def get_subscriber_queue_status(self, name: str) -> core.models.FillQueueStatus:
        """Get the pre-fill status of the given subscriber."""
        status = self._repo.set_subscriber_queue_status(name)
        return core.models.FillQueueStatus[status]

    async def set_subscriber_queue_status(self, name: str, status: core.models.FillQueueStatus):
        """Set the pre-fill status of the given subscriber."""
        await self._repo.set_subscriber_queue_status(name, status.name)

    async def remove_subscriber(self, name: str):
        """
        Delete a subscriber.
        """

        msg_repo = MessageRepository(self._repo._redis)

        await self._repo.delete_subscriber(name)
        await msg_repo.delete_queue(name)
