# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from univention.provisioning.backends_core.message import MQMessage
from univention.provisioning.backends_core.message_queue import Acknowledgements
from univention.provisioning.backends_core.nats_mq import NatsMessageQueue as NatsMessageQueue
from univention.provisioning.models.constants import DISPATCHER_SUBJECT_TEMPLATE
from univention.provisioning.models.message import Message

from .config import DispatcherSettings, dispatcher_settings
from .mq_port import MessageQueuePort


class NatsMessageQueueAdapter(MessageQueuePort):
    def __init__(self, settings: DispatcherSettings | None = None):
        self.settings = settings or dispatcher_settings()
        self.mq = NatsMessageQueue(self.settings)

    async def __aenter__(self) -> MessageQueuePort:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.close()
        return False

    async def connect(self) -> None:
        await self.mq.connect()

    async def close(self) -> None:
        await self.mq.close()

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str):
        return await self.mq.initialize_subscription(stream, manual_delete, subject)

    async def get_one_message(self, timeout: float) -> tuple[MQMessage, Acknowledgements]:
        return await self.mq.get_one_message(timeout=timeout)

    async def enqueue_message(self, queue: str, message: Message) -> None:
        await self.mq.add_message(queue, DISPATCHER_SUBJECT_TEMPLATE.format(subscription=queue), message.binary_dump())
