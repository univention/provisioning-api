# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Optional

from consumer.port import ConsumerPort

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus
from shared.models.queue import NatsMessage, Message


class PrefillKeys:
    def queue_name(subscriber_name: str) -> str:
        return f"prefill_{subscriber_name}"


class MessageService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        """Add the given message to the subscriber's prefill queue."""
        await self._port.add_message(PrefillKeys.queue_name(subscriber_name), message)

    async def delete_prefill_messages(self, subscriber_name: str):
        """Delete the pre-fill message from the subscriber's queue."""

        await self._port.delete_prefill_messages(subscriber_name)

    async def get_next_message(
        self,
        subscriber_name: str,
        pop: bool,
        timeout: float = 5,
        skip_prefill: Optional[bool] = False,
    ) -> Optional[NatsMessage]:
        """Retrieve the first message from the subscriber's stream.

        :param str subscriber_name: Name of the subscriber.
        :param bool pop: If the message should be deleted after request.
        :param float timeout: Max duration of the request before it expires.
        :param bool skip_prefill: List message, even if the pre-filling is not done?
        """

        response = await self.get_messages(
            subscriber_name, timeout, 1, pop, skip_prefill
        )
        return response[0] if response else None

    async def get_messages(
        self,
        subscriber_name: str,
        timeout: float,
        count: int,
        pop: bool,
        skip_prefill: Optional[bool] = False,
    ) -> List[NatsMessage]:
        """Return messages from a given queue.

        :param str subscriber_name: Name of the subscriber.
        :param float timeout: Max duration of the request before it expires.
        :param int count: How many messages to return at most.
        :param bool pop: If messages should be deleted after request.
        :param bool skip_prefill: List messages, even if the pre-filling is not done?
        """

        messages = []

        sub_service = SubscriptionService(self._port)
        queue_status = await sub_service.get_subscriber_queue_status(subscriber_name)

        # FIXME: fix logic to not get messages from prefill queue when empty

        if queue_status == FillQueueStatus.done:
            self.logger.info(
                "Getting the messages for the '%s' from the prefill queue",
                subscriber_name,
            )
            messages = await self._port.get_messages(
                PrefillKeys.queue_name(subscriber_name), timeout, count, pop
            )
            if not messages:
                await self._port.delete_stream(PrefillKeys.queue_name(subscriber_name))

        elif skip_prefill or len(messages) < count:
            self.logger.info(
                "Getting the messages for the '%s' from the main queue", subscriber_name
            )
            messages.extend(
                await self._port.get_messages(
                    subscriber_name, timeout, count - len(messages), pop
                )
            )

        return messages

    async def remove_message(self, msg: NatsMessage):
        """Remove a message from the subscriber's queue.

        :param msg: fetched message.
        """

        await self._port.remove_message(msg)
