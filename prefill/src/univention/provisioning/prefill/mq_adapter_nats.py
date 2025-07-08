# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from univention.provisioning.backends_core.message import MQMessage
from univention.provisioning.backends_core.message_queue import Acknowledgements
from univention.provisioning.backends_core.nats_mq import NatsMessageQueue as NatsMessageQueueAdapter
from univention.provisioning.models.constants import PREFILL_QUEUE_NAME, PREFILL_SUBJECT_TEMPLATE
from univention.provisioning.models.message import BaseMessage

from .config import PrefillSettings, prefill_settings
from .mq_port import MessageQueuePort

PREFILL_FAILURES_STREAM = "prefill-failures"
PREFILL_DURABLE_NAME = "prefill-service"


class NatsMessageQueue(MessageQueuePort):
    """
    Handle a message queue communication with NATS.

    Use as an async context manager.
    """

    def __init__(self, settings: PrefillSettings | None = None):
        self.settings = settings or prefill_settings()
        self.mq = NatsMessageQueueAdapter(self.settings)

    async def __aenter__(self) -> MessageQueuePort:
        await self.mq.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.mq.close()
        return False

    async def add_message_to_failures_queue(self, message: BaseMessage) -> None:
        await self.mq.add_message(PREFILL_FAILURES_STREAM, PREFILL_FAILURES_STREAM, message.binary_dump())

    async def add_message_to_queue(self, queue: str, message: BaseMessage) -> None:
        await self.mq.add_message(queue, PREFILL_SUBJECT_TEMPLATE.format(subscription=queue), message.binary_dump())

    async def get_one_message(self) -> tuple[MQMessage, Acknowledgements]:
        return await self.mq.get_one_message()

    async def initialize_subscription(self) -> None:
        await self.mq.initialize_subscription(PREFILL_QUEUE_NAME, False, None)

    async def prepare_failures_queue(self) -> None:
        await self.mq.ensure_stream(PREFILL_FAILURES_STREAM, False)
        await self.mq.ensure_consumer(PREFILL_FAILURES_STREAM)

    async def purge_queue(self, name: str) -> None:
        await self.mq.purge_stream(name, PREFILL_SUBJECT_TEMPLATE.format(subscription=name))
