# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Optional

from consumer.port import ConsumerPort

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus
from shared.models.queue import MQMessage, Message


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
    ) -> Optional[MQMessage]:
        """Retrieve the first message from the subscriber's stream.

        :param str subscriber_name: Name of the subscriber.
        :param bool pop: If the message should be deleted after request.
        :param float timeout: Max duration of the request before it expires.
        """

        response = await self.get_messages(subscriber_name, timeout, count=1, pop=pop)
        return response[0] if response else None

    async def get_messages(
        self,
        subscriber_name: str,
        timeout: float,
        count: int,
        pop: bool,
    ) -> List[MQMessage]:
        """Return messages from a given queue.

        :param str subscriber_name: Name of the subscriber.
        :param float timeout: Max duration of the request before it expires.
        :param int count: How many messages to return at most.
        :param bool pop: If messages should be deleted after request.
        """

        # TODO: Timeout of 0 leads to internal server error

        sub_service = SubscriptionService(self._port)
        queue_status = await sub_service.get_subscriber_queue_status(subscriber_name)

        messages = []
        prefill_stream = await self._port.stream_exists(
            PrefillKeys.queue_name(subscriber_name)
        )

        if queue_status == FillQueueStatus.done and prefill_stream:
            messages = await self.get_messages_from_prefill_queue(
                subscriber_name, timeout, count, pop
            )
        elif not prefill_stream:
            messages.extend(
                await self.get_messages_from_main_queue(
                    subscriber_name, timeout, count, pop
                )
            )

        return messages

    async def get_messages_from_main_queue(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        self.logger.info(
            "Getting the messages for the '%s' from the main queue", subscriber_name
        )
        return await self._port.get_messages(subscriber_name, timeout, count, pop)

    async def get_messages_from_prefill_queue(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        self.logger.info(
            "Getting the messages for the '%s' from the prefill queue", subscriber_name
        )
        prefill_queue_name = PrefillKeys.queue_name(subscriber_name)
        messages = await self._port.get_messages(
            prefill_queue_name, timeout, count, pop
        )
        if len(messages) < count:
            self.logger.info("All messages from the prefill queue have been delivered")
            messages.extend(
                await self.get_messages_from_main_queue(
                    subscriber_name, timeout, count - len(messages), pop
                )
            )
            if pop:
                await self._port.delete_stream(prefill_queue_name)
        return messages

    async def remove_message(self, msg: MQMessage):
        """Remove a message from the subscriber's queue.

        :param msg: fetched message.
        """

        await self._port.remove_message(msg)

    async def create_prefill_stream(self, subscriber_name: str):
        # delete the previously created stream if it exists
        await self._port.delete_stream(PrefillKeys.queue_name(subscriber_name))
        await self._port.create_stream(PrefillKeys.queue_name(subscriber_name))
