# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from typing import Optional

from .port import Port
from .subscriptions import SubscriptionService
from shared.models import (
    MessageProcessingStatusReport,
    MessageProcessingStatus,
    ProvisioningMessage,
    FillQueueStatus,
    Message,
    NewSubscription,
    PrefillMessage,
    PREFILL_SUBJECT_TEMPLATE,
    DISPATCHER_SUBJECT_TEMPLATE,
    DISPATCHER_STREAM,
    PREFILL_STREAM,
)


class MessageService:
    def __init__(self, port: Port):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def get_next_message(
        self,
        subscription_name: str,
        timeout: float,
        pop: bool,
    ) -> Optional[ProvisioningMessage]:
        """Retrieve the first message from the subscription's stream.

        :param str subscription_name: Name of the subscription.
        :param bool pop: If the message should be deleted after request.
        :param float timeout: Max duration of the request before it expires.
        """

        # TODO: Timeout of 0 leads to internal server error

        sub_service = SubscriptionService(self._port)
        queue_status = await sub_service.get_subscription_queue_status(
            subscription_name
        )

        if queue_status != FillQueueStatus.done:
            return None

        message = await self.get_messages_from_prefill_queue(
            subscription_name, timeout, pop
        )
        if message is None:
            self.logger.info(
                "All messages from the prefill subject have been delivered"
            )
            message = await self.get_messages_from_main_queue(
                subscription_name, timeout, pop
            )

        return message

    async def get_messages_from_main_queue(
        self, subscription: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        main_subject = DISPATCHER_SUBJECT_TEMPLATE.format(subscription=subscription)
        self.logger.info(
            "Getting the messages for the '%s' from the main subject", main_subject
        )
        return await self._port.get_message(subscription, main_subject, timeout, pop)

    async def get_messages_from_prefill_queue(
        self, subscription: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subscription=subscription)
        self.logger.info(
            "Getting the messages for the '%s' from the prefill subject",
            prefill_subject,
        )
        return await self._port.get_message(subscription, prefill_subject, timeout, pop)

    async def post_message_status(
        self, subscription_name: str, report: MessageProcessingStatusReport
    ):
        if report.status == MessageProcessingStatus.ok:
            await self._port.delete_message(subscription_name, report.message_seq_num)

    async def add_live_event(self, event: Message):
        await self._port.add_message(DISPATCHER_STREAM, DISPATCHER_STREAM, event)

    async def send_request_to_prefill(self, subscription: NewSubscription):
        self.logger.info("Sending the requests to prefill")
        message = PrefillMessage(
            publisher_name="consumer-registration",
            ts=datetime.now(),
            realms_topics=subscription.realms_topics,
            subscription_name=subscription.name,
        )
        await self._port.add_message(PREFILL_STREAM, PREFILL_STREAM, message)
