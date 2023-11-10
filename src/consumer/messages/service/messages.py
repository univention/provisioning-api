import logging
from datetime import datetime
from typing import List, Optional

import core.models

from consumer.messages.persistence.messages import MessageRepository
from consumer.subscriptions.persistence.subscriptions import SubscriptionRepository
from consumer.subscriptions.service.subscription import SubscriptionService
from core.models.queue import NatsMessage

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self, repo: MessageRepository):
        self._repo = repo

    async def publish_message(
        self,
        data: core.models.NewMessage,
        publisher_name: str,
        ts: Optional[datetime] = None,
    ):
        """Publish the given message to all subscribers
           to the given message type.

        :param dict content: Key-value pairs to sent to the consumer.
        :param str publisher_name: The name of the publisher.
        :param datetime ts: Optional timestamp to be assigned to the message.
        """

        message = core.models.Message(
            publisher_name=publisher_name,
            ts=ts or datetime.utcnow(),
            realm=data.realm,
            topic=data.topic,
            body=data.body,
        )

        service = SubscriptionService(
            SubscriptionRepository(self._repo.redis, self._repo.nats)
        )

        subscriber_names = await service.get_subscribers_for_topic(
            message.realm, message.topic
        )
        for subscriber_name in subscriber_names:
            await self._repo.add_live_message(subscriber_name, message)

    async def add_prefill_message(
        self, subscriber_name: str, message: core.models.Message
    ):
        """Add the given message to the subscriber's queue."""
        await self._repo.add_prefill_message(subscriber_name, message)

    async def delete_prefill_messages(self, subscriber_name: str):
        """Delete the pre-fill message from the subscriber's queue."""

        service = MessageService(self._repo)
        service.delete_prefill_messages(subscriber_name)

    async def get_next_message(
        self,
        subscriber_name: str,
        pop: bool,
        timeout: float = 5,
        force: Optional[bool] = False,
    ) -> Optional[NatsMessage]:
        """Retrieve the first message from the subscriber's stream.

        :param str subscriber_id: Id of the subscriber.
        :param int block: How long to block in milliseconds waiting for messages.
        :param bool force: List messages, even if the pre-filling is not done?
        """

        sub_service = SubscriptionService(
            SubscriptionRepository(self._repo.redis, self._repo.nats)
        )
        queue_status = await sub_service.get_subscriber_queue_status(subscriber_name)

        if force or (queue_status == core.models.FillQueueStatus.done):
            return await self._repo.get_next_message(subscriber_name, timeout, pop)
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

        :param str subscriber_id: Id of the subscriber.
        :param int count: How many messages to return at most.
        :param str first: Id of the first message to return.
        :param str last: Id of the last message to return.
        :param bool force: List messages, even if the pre-filling is not done?
        """

        sub_service = SubscriptionService(
            SubscriptionRepository(self._repo.redis, self._repo.nats)
        )
        queue_status = await sub_service.get_subscriber_queue_status(subscriber_name)

        if force or (queue_status == core.models.FillQueueStatus.done):
            return await self._repo.get_messages(subscriber_name, timeout, count, pop)
        else:
            return []

    async def remove_message(self, msg: NatsMessage):
        """Remove a message from the subscriber's queue.

        :param str subscriber_id: Id of the subscriber.
        :param str message_id: Id of the message to delete.
        """

        await self._repo.delete_message(msg)

    async def remove_queue(self, subscriber_name: str):
        """Delete the entire queue for the given consumer.

        :param str subscriber_id: Id of the subscriber.
        """

        await self._repo.delete_queue(subscriber_name)
