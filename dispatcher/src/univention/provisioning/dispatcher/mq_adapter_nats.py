# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Optional

from univention.provisioning.backends import message_queue
from univention.provisioning.backends.message_queue import Acknowledgements
from univention.provisioning.backends.nats_mq import BaseQueue
from univention.provisioning.models.message import Message, MQMessage

from .config import DispatcherSettings, dispatcher_settings
from .mq_port import MessageQueuePort


class NatsMessageQueueAdapter(MessageQueuePort):
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        super().__init__(settings or dispatcher_settings())
        self.mq = message_queue(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )

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

    async def initialize_subscription(self, queue: BaseQueue):
        return await self.mq.initialize_subscription(queue)

    async def get_one_message(self, timeout: float) -> tuple[MQMessage, Acknowledgements]:
        return await self.mq.get_one_message(timeout=timeout)

    async def enqueue_message(self, queue: BaseQueue, message: Message) -> None:
        await self.mq.add_message(queue, message)

    async def stream_exists(self, queue: BaseQueue) -> bool:
        return await self.mq.stream_exists(queue)
