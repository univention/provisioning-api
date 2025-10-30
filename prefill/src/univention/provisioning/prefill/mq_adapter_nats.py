# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import Optional, Tuple

from univention.provisioning.backends import message_queue
from univention.provisioning.backends.message_queue import Acknowledgements
from univention.provisioning.backends.nats_mq import BaseQueue
from univention.provisioning.models.message import BaseMessage, MQMessage

from .config import PrefillSettings, prefill_settings
from .mq_port import MessageQueuePort
from .retry_helper import retry

PREFILL_FAILURES_STREAM = "prefill-failures"
PREFILL_DURABLE_NAME = "prefill-service"

logger = logging.getLogger(__name__)


class NatsMessageQueue(MessageQueuePort):
    """
    Handle a message queue communication with NATS.

    Use as an async context manager.
    """

    def __init__(self, settings: Optional[PrefillSettings] = None):
        super().__init__(settings or prefill_settings())
        self.mq = message_queue(
            server=self.settings.nats_server,
            user=settings.nats_user,
            password=settings.nats_password,
            max_reconnect_attempts=settings.nats_max_reconnect_attempts,
        )

    async def __aenter__(self) -> MessageQueuePort:
        await self.mq.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.mq.close()
        return False

    @retry(logger=logger)
    async def add_message(self, queue: BaseQueue, message: BaseMessage) -> None:
        await self.mq.add_message(queue, message)

    async def get_one_message(self) -> Tuple[MQMessage, Acknowledgements]:
        return await self.mq.get_one_message()

    async def initialize_subscription(self, queue: BaseQueue) -> None:
        await self.mq.initialize_subscription(queue)

    async def prepare_failures_queue(self, queue: BaseQueue) -> None:
        await self.mq.ensure_stream(queue)
        await self.mq.ensure_consumer(queue)

    async def purge_queue(self, queue: BaseQueue) -> None:
        await self.mq.purge_stream(queue)
