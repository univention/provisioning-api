# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from .port import Port

from .subscriptions import SubscriptionService
from shared.models import (
    MessageProcessingStatusReport,
    MessageProcessingStatus,
    PublisherName,
    ProvisioningMessage,
    FillQueueStatus,
    Message,
    NewSubscription,
    PrefillMessage,
)

PREFILL_SUBJECT_TEMPLATE = "prefill_{subject}"


class MessageService:
    def __init__(self, port: Port):
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
    ) -> Optional[ProvisioningMessage]:
        """Retrieve the first message from the subscription's stream.

        :param str subscription_name: Name of the subscription.
        :param bool pop: If the message should be deleted after request.
        :param float timeout: Max duration of the request before it expires.
        """

        response = await self.get_messages(subscription_name, timeout, count=1, pop=pop)
        return response[0] if response else None

    async def get_messages(
        self,
        subscription_name: str,
        timeout: float,
        count: int,
        pop: bool,
    ) -> List[ProvisioningMessage]:
        """Return messages from a given queue.

        :param str subscription_name: Name of the subscription.
        :param float timeout: Max duration of the request before it expires.
        :param int count: How many messages to return at most.
        :param bool pop: If messages should be deleted after request.
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
        elif not prefill_stream:
            messages.extend(
                await self.get_messages_from_main_queue(
                    subscription_name, timeout, count, pop
                )
            )

        return messages

    async def get_messages_from_main_queue(
        self, subject: str, timeout: float, count: int, pop: bool
    ) -> List[ProvisioningMessage]:
        self.logger.info(
            "Getting the messages for the '%s' from the main queue", subject
        )
        return await self._port.get_messages(subject, timeout, count, pop)

    async def get_messages_from_prefill_queue(
        self, subject: str, timeout: float, count: int, pop: bool
    ) -> List[ProvisioningMessage]:
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

    async def post_messages_status(
        self, subscription_name: str, reports: List[MessageProcessingStatusReport]
    ):
        tasks = [
            self.delete_message(subscription_name, report)
            for report in reports
            if report.status == MessageProcessingStatus.ok
        ]
        # Gather all tasks and run them concurrently
        await asyncio.gather(*tasks)

    async def delete_message(
        self, subscription_name: str, report: MessageProcessingStatusReport
    ):
        """Delete the messages from the subscriber's queue."""

        if report.publisher_name == PublisherName.udm_pre_fill:
            stream_name = PREFILL_SUBJECT_TEMPLATE.format(subject=subscription_name)
        else:
            stream_name = subscription_name

        await self._port.delete_message(stream_name, report.message_seq_num)

    async def create_prefill_stream(self, subscription_name: str):
        # delete the previously created stream if it exists
        prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subject=subscription_name)
        await self._port.delete_stream(prefill_subject)
        await self._port.create_stream(prefill_subject)

    async def add_message(self, name: str, msg: Message):
        await self._port.add_message(name, msg)

    async def add_live_event(self, event: Message):
        # TODO: define the name "incoming" globally or handle it differently alltogether

        await self._port.add_message("incoming", event)

    async def send_request_to_prefill(self, subscription: NewSubscription):
        self.logger.info("Sending the requests to prefill")
        message = PrefillMessage(
            publisher_name="consumer-registration",
            ts=datetime.now(),
            realms_topics=subscription.realms_topics,
            subscription_name=subscription.name,
        )
        await self._port.add_message("prefill", message)
