import re
from typing import List

import shared.models
from consumer.messages.persistence.messages import MessageRepository
from consumer.port import Port
from consumer.subscriptions.persistence.subscriptions import SubscriptionRepository


def match_subscription(
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

    async def get_subscribers(self) -> List[shared.models.Subscriber]:
        """
        Return a list of names of all known subscribers.
        """

        names = await self._repo.get_subscriber_names()
        subscribers = [await self.get_subscriber(name) for name in names]
        return subscribers

    async def get_subscriber(self, name: str) -> shared.models.Subscriber:
        """
        Get information about a registered subscriber.
        """

        data = await self._repo.get_subscriber(name)
        return shared.models.Subscriber.model_validate(data)

    async def get_subscribers_for_topic(self, realm: str, topic: str) -> List[str]:
        """
        Return a list names of everyone subscribed to a given realm and topic.
        """

        return [
            s_name
            for s_realm, s_topic, s_name in await self._repo.get_subscribers_by_topics()
            if match_subscription(s_realm, s_topic, realm, topic)
        ]

    async def add_subscriber(self, sub: shared.models.NewSubscriber):
        """
        Add a new subscriber.
        """

        if sub.fill_queue:
            fill_queue_status = shared.models.FillQueueStatus.pending
        else:
            fill_queue_status = shared.models.FillQueueStatus.done

        await self._repo.add_subscriber(
            name=sub.name,
            realms_topics=sub.realms_topics,
            fill_queue=sub.fill_queue,
            fill_queue_status=fill_queue_status,
        )

    async def get_subscriber_queue_status(
        self, name: str
    ) -> shared.models.FillQueueStatus:
        """Get the pre-fill status of the given subscriber."""
        status = await self._repo.get_subscriber_queue_status(name)
        return shared.models.FillQueueStatus[status]

    async def set_subscriber_queue_status(
        self, name: str, status: shared.models.FillQueueStatus
    ):
        """Set the pre-fill status of the given subscriber."""
        await self._repo.set_subscriber_queue_status(name, status.name)

    async def remove_subscriber(self, name: str):
        """
        Delete a subscriber.
        """

        msg_repo = MessageRepository(Port())

        await self._repo.delete_subscriber(name)
        await msg_repo.delete_queue(name)
