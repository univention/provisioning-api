# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Optional

from consumer.port import ConsumerPort

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus, MQMessage, Message


PREFILL_SUBJECT_TEMPLATE = "prefill_{subject}"


class MessageService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def add_prefill_message(self, subscription_name: str, message: Message):
        """Add the given message to the subscription's prefill queue."""
        await self._port.add_message(
            PREFILL_SUBJECT_TEMPLATE.format(subject=subscription_name), message
        )

    async def delete_prefill_messages(self, subscription_name: str):
        """Delete the pre-fill message from the subscription's queue."""

        await self._port.delete_prefill_messages(
            PREFILL_SUBJECT_TEMPLATE.format(subject=subscription_name)
        )

    async def get_next_message(
        self,
        subscription_name: str,
        pop: bool,
        timeout: float = 5,
        skip_prefill: Optional[bool] = False,
    ) -> Optional[MQMessage]:
        """Retrieve the first message from the subscription's stream.

        :param str subscription_name: Name of the subscription.
        :param bool pop: If the message should be deleted after request.
        :param float timeout: Max duration of the request before it expires.
        :param bool skip_prefill: List message, even if the pre-filling is not done?
        """

        response = await self.get_messages(
            subscription_name, timeout, count=1, pop=pop, skip_prefill=skip_prefill
        )
        return response[0] if response else None

    async def get_messages(
        self,
        subscription_name: str,
        timeout: float,
        count: int,
        pop: bool,
        skip_prefill: Optional[bool],
    ) -> List[MQMessage]:
        """Return messages from a given queue.

        :param str subscription_name: Name of the subscription.
        :param float timeout: Max duration of the request before it expires.
        :param int count: How many messages to return at most.
        :param bool pop: If messages should be deleted after request.
        :param bool skip_prefill: List messages, even if the pre-filling is not done?
        """

        # TODO: Timeout of 0 leads to internal server error

        sub_service = SubscriptionService(self._port)
        queue_status = await sub_service.get_subscription_queue_status(
            subscription_name
        )

        messages = []
        prefill_stream = await self._port.stream_exists(
            PREFILL_SUBJECT_TEMPLATE.format(subject=subscription_name)
        )

        if queue_status == FillQueueStatus.done and prefill_stream:
            messages = await self.get_messages_from_prefill_queue(
                subscription_name, timeout, count, pop
            )
        elif skip_prefill or not prefill_stream:
            messages.extend(
                await self.get_messages_from_main_queue(
                    subscription_name, timeout, count, pop
                )
            )

        return messages

    async def get_messages_from_main_queue(
        self, subject: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        self.logger.info(
            "Getting the messages for the '%s' from the main queue", subject
        )
        return await self._port.get_messages(subject, timeout, count, pop)

    async def get_messages_from_prefill_queue(
        self, subject: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        self.logger.info(
            "Getting the messages for the '%s' from the prefill queue", subject
        )
        prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subject=subject)
        messages = await self._port.get_messages(prefill_subject, timeout, count, pop)
        if len(messages) < count:
            self.logger.info("All messages from the prefill queue have been delivered")
            messages.extend(
                await self.get_messages_from_main_queue(
                    subject, timeout, count - len(messages), pop
                )
            )
            if pop:
                await self._port.delete_stream(prefill_subject)
        return messages

    async def remove_message(self, msg: MQMessage):
        """Remove a message from the subscription's queue.

        :param msg: fetched message.
        """

        await self._port.remove_message(msg)

    async def create_prefill_stream(self, subscription_name: str):
        # delete the previously created stream if it exists
        prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subject=subscription_name)
        await self._port.delete_stream(prefill_subject)
        await self._port.create_stream(prefill_subject)

    async def add_message(self, name: str, msg: Message):
        await self._port.add_message(name, msg)
