import re
from typing import List

from consumer.port import ConsumerPort
from shared.models import Subscriber, NewSubscriber, FillQueueStatus


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
    def __init__(self, port: ConsumerPort):
        self._port = port

    async def get_subscribers(self) -> List[Subscriber]:
        """
        Return a list of names of all known subscribers.
        """

        names = await self._port.get_subscriber_names()
        subscribers = [await self.get_subscriber(name) for name in names]
        return subscribers

    async def get_subscriber(self, name: str) -> Subscriber:
        """
        Get information about a registered subscriber.
        """
        sub = await self._port.get_subscriber_info(name)
        if not sub:
            raise ValueError("Subscriber not found.")

        data = dict(
            name=sub["name"],
            realms_topics=sub["realms_topics"],
            fill_queue=bool(int(sub["fill_queue"])),
            fill_queue_status=sub["fill_queue_status"],
        )

        return Subscriber.model_validate(data)

    async def add_subscriber(self, sub: NewSubscriber):
        """
        Add a new subscriber.
        """

        if sub.fill_queue:
            fill_queue_status = FillQueueStatus.pending
        else:
            fill_queue_status = FillQueueStatus.done

        if await self._port.get_subscriber_info(sub.name):
            raise ValueError("Subscriber already exists.")

        await self._port.add_subscriber(
            sub.name, sub.realms_topics, sub.fill_queue, fill_queue_status
        )

    async def get_subscriber_queue_status(self, name: str) -> FillQueueStatus:
        """Get the pre-fill status of the given subscriber."""

        sub_info = await self._port.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber not found.")

        status = sub_info["fill_queue_status"]
        return FillQueueStatus[status]

    async def set_subscriber_queue_status(self, name: str, status: FillQueueStatus):
        """Set the pre-fill status of the given subscriber."""
        sub_info = await self._port.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber not found.")

        sub_info["fill_queue_status"] = status.name
        await self._port.set_subscriber_queue_status(name, sub_info)

    async def delete_subscriber(self, name: str):
        """
        Delete a subscriber and all of its data.
        """

        if not await self._port.get_subscriber_info(name):
            raise ValueError("Subscriber not found.")

        await self._port.delete_subscriber(name)
        await self._port.delete_queue(name)
