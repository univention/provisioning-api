from typing import Annotated, List, Optional

import fastapi
from consumer.port import Port, PortDependency
from shared.models import Message

from shared.models.queue import NatsMessage


class MessageRepository:
    """Store and retrieve messages from Redis."""

    def __init__(self, port: Port):
        self.port = port

    async def add_live_message(self, subscriber_name: str, message: Message):
        """Enqueue the given message for a particular subscriber.

        The message is received "live" and placed at the end of the queue
        (i.e. with the current timestamp).

        :param str subscriber_name: Name of the subscriber.
        :param Message message: The message from the publisher.
        """

        await self.port.add_live_message(subscriber_name, message)

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        """Enqueue the given message for a particular subscriber.

        The message originates from the pre-fill process and is queued
        ahead of (== earlier than) live messages.

        :param str subscriber_name: Name of the subscriber.
        :param Message message: The message from the pre-fill task.
        """
        await self.port.add_prefill_message(subscriber_name, message)

    async def delete_prefill_messages(self, subscriber_name: str):
        """Delete all pre-fill messages from the subscriber's queue.

        :param str subscriber_name: name of the subscriber.
        """
        await self.port.delete_prefill_messages(subscriber_name)

    async def get_next_message(
        self, subscriber_name: str, timeout: float, pop: bool
    ) -> Optional[NatsMessage]:
        """Retrieve the first message from the subscriber's stream.

        :param str subscriber_name: name of the subscriber.
        :param float timeout: Max duration of the request before it expires.
        """
        response = await self.port.get_next_message(subscriber_name, timeout, pop)
        if not response:
            # empty stream
            return None

        return response[0]

        response = await self.port.get_next_message(subscriber_name, timeout)
        if not response:
            # empty stream
            return None

        return response[0]

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        """Return messages from a given queue.

        By default, *all* messages will be returned unless further restricted by
        parameters.

        :param str subscriber_name: name of the subscriber.
        :param float timeout: Max duration of the request before it expires.
        :param int count: How many messages to return at most.
        :param bool pop: If messages should be deleted after request.
        """
        return await self.port.get_messages(subscriber_name, timeout, count, pop)

    async def delete_message(self, msg: NatsMessage):
        """Remove a message from the subscriber's queue.

        :param List[Msg] msgs: set of fetched messages.
        """
        await self.port.delete_message(msg)

    async def delete_queue(self, subscriber_name: str):
        """Delete the entire queue for the given consumer.

        :param str subscriber_name: Name of the subscriber.
        """

        await self.port.delete_queue(subscriber_name)


def get_message_repository(port: PortDependency) -> MessageRepository:
    return MessageRepository(port)


DependsMessageRepo = Annotated[
    MessageRepository, fastapi.Depends(get_message_repository)
]
