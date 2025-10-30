# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
from typing import Optional

from nats.js.errors import NotFoundError

from univention.provisioning.backends import message_queue
from univention.provisioning.backends.message_queue import MessageQueue
from univention.provisioning.models.constants import (
    DISPATCHER_QUEUE_NAME,
    DISPATCHER_SUBJECT_TEMPLATE,
    PREFILL_SUBJECT_TEMPLATE,
    PublisherName,
)
from univention.provisioning.models.message import Message, PrefillMessage, ProvisioningMessage
from univention.provisioning.models.subscription import NewSubscription

from ..backends.nats_mq import ConsumerQueue, IncomingQueue, PrefillQueue
from .config import AppSettings, app_settings
from .exceptions import ProvisioningBackendError
from .mq_port import MessageQueuePort

PREFILL_FAILURES_STREAM = "prefill-failures"
PREFILL_DURABLE_NAME = "prefill-service"


class NatsMessageQueue(MessageQueuePort):
    """
    Handle a message queue communication with NATS.

    Use as an async context manager.
    """

    def __init__(self, settings: Optional[AppSettings] = None):
        super().__init__(settings or app_settings())
        self.mq: Optional[MessageQueue] = None

    async def __aenter__(self) -> MessageQueuePort:
        self.mq = message_queue(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
        )
        await self.mq.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.mq.close()
        self.mq = None
        return False

    async def enqueue_for_dispatcher(self, message: Message) -> None:
        await self.mq.add_message(ConsumerQueue(DISPATCHER_QUEUE_NAME), message)

    async def get_messages_from_main_queue(
        self, subscription: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        try:
            return await self.mq.get_message(IncomingQueue(subscription), timeout, pop)
        except NotFoundError as err:
            raise ProvisioningBackendError(str(err))

    async def get_messages_from_prefill_queue(
        self, subscription: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        try:
            return await self.mq.get_message(ConsumerQueue(subscription), timeout, pop)
        except NotFoundError as err:
            raise ProvisioningBackendError(str(err))

    async def delete_message(self, stream: str, seq_num: int):
        await self.mq.delete_message(stream, seq_num)

    async def create_queue(self, queue):
        await self.mq.ensure_stream(queue)

    async def delete_queue(self, queue) -> None:
        await self.mq.delete_stream(queue)
        await self.mq.delete_consumer(queue)

    async def create_consumer(self, queue):
        await self.mq.ensure_consumer(queue)

    async def delete_consumer(self, queue):
        await self.mq.delete_consumer(queue)

    async def prepare_new_consumer_queue(self, consumer_name: str):
        await self.create_queue(
            consumer_name,
            True,
            [
                DISPATCHER_SUBJECT_TEMPLATE.format(subscription=consumer_name),
                PREFILL_SUBJECT_TEMPLATE.format(subscription=consumer_name),
            ],
        )

    async def request_prefill(self, subscription: NewSubscription):
        message = PrefillMessage(
            publisher_name=PublisherName.consumer_registration,
            ts=datetime.now(),
            realms_topics=subscription.realms_topics,
            subscription_name=subscription.name,
        )
        await self.mq.add_message(PrefillQueue(), message)
