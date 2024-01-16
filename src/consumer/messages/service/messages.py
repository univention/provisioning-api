# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import logging
from typing import List, Optional

from consumer.port import ConsumerPort

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus
from shared.models.queue import MQMessage, Message


class MessageService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

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
    ) -> Optional[MQMessage]:
        """Retrieve the first message from the subscriber's stream.

        :param str subscriber_name: Name of the subscriber.
        :param bool pop: If messages should be deleted after request.
        :param float timeout: Max duration of the request before it expires.
        :param bool force: List messages, even if the pre-filling is not done?
        """

        response = await self.get_messages(subscriber_name, timeout, 1, pop, force)
        return response[0] if response else None

    async def get_messages(
        self,
        subscriber_name: str,
        timeout: float,
        count: int,
        pop: bool,
        force: Optional[bool] = False,
    ) -> List[MQMessage]:
        """Return messages from a given queue.

        :param str subscriber_name: Name of the subscriber.
        :param float timeout: Max duration of the request before it expires.
        :param int count: How many messages to return at most.
        :param bool pop: If messages should be deleted after request.
        :param bool force: List messages, even if the pre-filling is not done?
        """

        sub_service = SubscriptionService(self._port)
        queue_status = await sub_service.get_subscriber_queue_status(subscriber_name)

        if not force:
            while queue_status not in (FillQueueStatus.done, FillQueueStatus.failed):
                await asyncio.sleep(0.1)
                logging.info(
                    "Waiting for pre-filling to finish for subscriber %s. Current status: %s",
                    subscriber_name,
                    queue_status,
                )
                queue_status = await sub_service.get_subscriber_queue_status(
                    subscriber_name
                )

        response = await self._port.get_messages(subscriber_name, timeout, count, pop)
        return response

    async def remove_message(self, msg: MQMessage):
        """Remove a message from the subscriber's queue.

        :param msg: fetched message.
        """

        await self._port.remove_message(msg)

    async def delete_queue(self, subscriber_name: str):
        """Delete the entire queue for the given consumer.

        :param str subscriber_name: Name of the subscriber.
        """

        await self._port.delete_queue(subscriber_name)
