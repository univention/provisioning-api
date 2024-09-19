# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging
import time
from datetime import datetime
from typing import Optional

from univention.provisioning.models import (
    DISPATCHER_STREAM,
    DISPATCHER_SUBJECT_TEMPLATE,
    PREFILL_STREAM,
    PREFILL_SUBJECT_TEMPLATE,
    FillQueueStatus,
    Message,
    MessageProcessingStatus,
    MessageProcessingStatusReport,
    NewSubscription,
    PrefillMessage,
    ProvisioningMessage,
    PublisherName,
)

from .port import Port
from .subscriptions import SubscriptionService

logger = logging.getLogger(__name__)


class MessageService:
    _subscription_prefill_done: dict[str, bool] = {}

    def __init__(self, port: Port):
        self._port = port

    async def check_subscription_status(self, subscription_name: str, timeout: float) -> FillQueueStatus:
        sub_service = SubscriptionService(self._port)
        loop = asyncio.get_event_loop()
        end_time = loop.time() + timeout
        while loop.time() < end_time:
            queue_status = await sub_service.get_subscription_queue_status(subscription_name)
            if queue_status == FillQueueStatus.done:
                return queue_status
            await asyncio.sleep(1)

        return await sub_service.get_subscription_queue_status(subscription_name)

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
        timeout = max(timeout, 0.1)  # Timeout of 0 leads to internal server error
        t0 = time.perf_counter()
        if self._subscription_prefill_done.get(subscription_name, False):
            message = await self.get_messages_from_main_queue(subscription_name, timeout, pop)
            queue = "main"
        else:
            if await self.check_subscription_status(subscription_name, timeout) != FillQueueStatus.done:  # take ~1.5ms
                logger.warning(
                    "Prefill status for subscription %r did not reach 'done' within the timeout period.",
                    subscription_name,
                )
                return None

            message = await self.get_messages_from_prefill_queue(subscription_name, timeout, pop)
            queue = "prefill"
            if message is None:
                logger.info(
                    "All messages from the prefill subject for %r have been delivered. Will not check again.",
                    subscription_name,
                )
                self._subscription_prefill_done[subscription_name] = True
        logger.debug(
            "Retrieved%s message from %s queue for %r. (%.1f ms)",
            " a" if message else " no",
            queue,
            subscription_name,
            (time.perf_counter() - t0) * 1000,
        )
        return message

    async def get_messages_from_main_queue(
        self, subscription: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        main_subject = DISPATCHER_SUBJECT_TEMPLATE.format(subscription=subscription)
        return await self._port.get_message(subscription, main_subject, timeout, pop)

    async def get_messages_from_prefill_queue(
        self, subscription: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subscription=subscription)
        return await self._port.get_message(subscription, prefill_subject, timeout, pop)

    async def post_message_status(self, subscription_name: str, seq_num: int, report: MessageProcessingStatusReport):
        if report.status == MessageProcessingStatus.ok:
            await self._port.delete_message(subscription_name, seq_num)

    async def add_live_event(self, event: Message):
        await self._port.add_message(DISPATCHER_STREAM, DISPATCHER_STREAM, event)

    async def send_request_to_prefill(self, subscription: NewSubscription):
        logger.info("Sending the requests to prefill")
        message = PrefillMessage(
            publisher_name=PublisherName.consumer_registration,
            ts=datetime.now(),
            realms_topics=subscription.realms_topics,
            subscription_name=subscription.name,
        )
        await self._port.add_message(PREFILL_STREAM, PREFILL_STREAM, message)
