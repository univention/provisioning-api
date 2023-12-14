import logging
from typing import List, Optional

from consumer.port import ConsumerPort

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus
from shared.models.queue import NatsMessage, Message

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self, port: ConsumerPort):
        self._port = port

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        """Add the given message to the subscriber's queue."""
        await self._port.add_prefill_message(subscriber_name, message)

    async def delete_prefill_messages(self, subscriber_name: str):
        """Delete the pre-fill message from the subscriber's queue."""

        await self._port.delete_prefill_messages(subscriber_name)

    async def get_next_message(
        self,
        subscriber_name: str,
        pop: bool,
        timeout: float = 5,
        force: Optional[bool] = False,
    ) -> Optional[NatsMessage]:
        """Retrieve the first message from the subscriber's stream.

        :param str subscriber_name: Name of the subscriber.
        :param bool pop: If messages should be deleted after request.
        :param float timeout: Max duration of the request before it expires.
        :param bool force: List messages, even if the pre-filling is not done?
        """

        sub_service = SubscriptionService(self._port)
        queue_status = await sub_service.get_subscriber_queue_status(subscriber_name)

        if force or (queue_status == FillQueueStatus.done):
            response = await self._port.get_next_message(subscriber_name, timeout, pop)
            return response[0] if response else None
        else:
            # TODO: if `block` is set this call should block until the queue is ready
            return None

    async def get_messages(
        self,
        subscriber_name: str,
        timeout: float,
        count: int,
        pop: bool,
        force: Optional[bool] = False,
    ) -> List[NatsMessage]:
        """Return messages from a given queue.

        By default, *all* messages will be returned unless further restricted by
        parameters.

        :param str subscriber_name: Name of the subscriber.
        :param float timeout: Max duration of the request before it expires.
        :param int count: How many messages to return at most.
        :param bool pop: If messages should be deleted after request.
        :param bool force: List messages, even if the pre-filling is not done?
        """

        sub_service = SubscriptionService(self._port)
        queue_status = await sub_service.get_subscriber_queue_status(subscriber_name)

        if force or (queue_status == FillQueueStatus.done):
            logger.info(f"Getting the messages for the '{subscriber_name}'")
            return await self._port.get_messages(subscriber_name, timeout, count, pop)
        else:
            return []

    async def remove_message(self, msg: NatsMessage):
        """Remove a message from the subscriber's queue.

        :param msg: fetched message.
        """

        await self._port.remove_message(msg)

    async def delete_queue(self, subscriber_name: str):
        """Delete the entire queue for the given consumer.

        :param str subscriber_name: Name of the subscriber.
        """

        await self._port.delete_queue(subscriber_name)
