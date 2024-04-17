# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import logging
from typing import Optional, Dict

from server.adapters.nats_adapter import NatsMQAdapter, NatsKVAdapter
from shared.models import Message, MQMessage, Bucket

from .config import DispatcherSettings

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        self.settings = settings or DispatcherSettings()
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.mq_adapter.connect(
            user=port.settings.nats_user,
            password=port.settings.nats_password,
            max_reconnect_attempts=port.settings.max_reconnect_attempts,
        )
        await port.kv_adapter.init(
            buckets=[Bucket.subscriptions],
            user=port.settings.nats_user,
            password=port.settings.nats_password,
        )

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()

    async def send_message_to_subscription(
        self, stream: str, subject: str, message: Message
    ):
        await self.mq_adapter.add_message(stream, subject, message)

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.mq_adapter.subscribe_to_queue(subject, deliver_subject)

    async def wait_for_event(self) -> MQMessage:
        return await self.mq_adapter.wait_for_event()

    async def acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message(message)

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_in_progress(message)

    async def watch_for_changes(self, subscriptions: Dict[str, list]):
        await self.kv_adapter.watch_for_changes(subscriptions)
