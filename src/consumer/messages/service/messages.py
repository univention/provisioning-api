# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import base64
import logging
from typing import List, Optional

from consumer.port import ConsumerPort

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus
from shared.models.queue import NatsMessage, Message, PrefillStream


class PrefillKeys:
    def queue_name(subscription_name: str) -> str:
        return f"prefill_{subscription_name}"


class MessageService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        """Add the given message to the subscriber's prefill queue."""
        encoded_realm_topic = base64.b64encode(
            f"{message.realm}:{message.topic}".encode()
        ).decode()
        queue_name = f"{subscriber_name}_{encoded_realm_topic}"
        await self._port.add_message(PrefillKeys.queue_name(queue_name), message)

    async def delete_prefill_messages(self, queue_name: str):
        """Delete the pre-fill message from the subscriber's queue."""

        await self._port.delete_prefill_messages(queue_name)

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
            subscriber_name, timeout, count=1, pop=pop, skip_prefill=skip_prefill
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

        sub_service = SubscriptionService(self._port)
        subscriptions = await sub_service.get_subscription_names(subscriber_name)

        messages = []
        for sub in subscriptions:
            queue_name = f"{subscriber_name}_{sub}"
            queue_status = await sub_service.get_subscription_queue_status(queue_name)

            prefill_stream = await self._port.stream_exists(
                PrefillKeys.queue_name(queue_name)
            )

            if queue_status == FillQueueStatus.done and prefill_stream:
                messages.extend(
                    await self.get_messages_from_prefill_queue(
                        queue_name, timeout, count, pop
                    )
                )
            elif skip_prefill or not prefill_stream:
                messages.extend(
                    await self.get_messages_from_main_queue(
                        queue_name, timeout, count, pop
                    )
                )
            if len(messages) == count:
                break

        return messages

    async def get_messages_from_main_queue(
        self, queue_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        self.logger.info("Getting the messages from the main queue: '%s'", queue_name)
        return await self._port.get_messages(queue_name, timeout, count, pop)

    async def get_messages_from_prefill_queue(
        self, queue_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        prefill_queue_name = PrefillKeys.queue_name(queue_name)
        self.logger.info(
            "Getting the messages from the prefill queue: '%s'", prefill_queue_name
        )
        messages = await self._port.get_messages(
            prefill_queue_name, timeout, count, pop
        )
        if len(messages) < count and pop:
            self.logger.info("All messages from the prefill queue have been delivered")
            await self._port.delete_stream(prefill_queue_name)
            messages.extend(
                await self.get_messages_from_main_queue(
                    queue_name, timeout, count - len(messages), pop
                )
            )
        return messages

    async def remove_message(self, msg: NatsMessage):
        """Remove a message from the subscriber's queue.

        :param msg: fetched message.
        """

        await self._port.remove_message(msg)

    async def create_prefill_stream(self, data: PrefillStream):
        encoded_realm_topic = base64.b64encode(
            f"{data.realm}:{data.topic}".encode()
        ).decode()
        queue_name = f"{data.subscriber_name}_{encoded_realm_topic}"
        # delete the previously created stream if it exists
        await self._port.delete_stream(PrefillKeys.queue_name(queue_name))
        await self._port.create_stream(PrefillKeys.queue_name(queue_name))
        await self._port.create_consumer(PrefillKeys.queue_name(queue_name))

    async def add_message(self, name: str, msg: Message):
        encoded_realm_topic = base64.b64encode(
            f"{msg.realm}:{msg.topic}".encode()
        ).decode()
        queue_name = f"{name}_{encoded_realm_topic}"
        await self._port.add_message(queue_name, msg)
