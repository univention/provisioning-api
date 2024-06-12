# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import logging
from typing import Optional, Dict

from server.adapters.nats_adapter import NatsMessageQueue, NatsKVStore
from server.adapters.ports import KVStore, MessageQueue
from univention.provisioning.models import Message, MQMessage, Bucket

from .config import DispatcherSettings

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        self.settings = settings or DispatcherSettings()
        self.mq: MessageQueue = NatsMessageQueue()
        self.kv: KVStore = NatsKVStore()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.mq.connect(
            server=port.settings.nats_server,
            user=port.settings.nats_user,
            password=port.settings.nats_password,
            max_reconnect_attempts=port.settings.max_reconnect_attempts,  # unexpected argument
        )
        await port.kv.init(
            buckets=[Bucket.subscriptions],
            user=port.settings.nats_user,
            password=port.settings.nats_password,
        )

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq.close()
        await self.kv.close()

    async def send_message_to_subscription(
        self, stream: str, subject: str, message: Message
    ):
        await self.mq.add_message(stream, subject, message)

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.mq.subscribe_to_queue(subject, deliver_subject)

    async def wait_for_event(self) -> MQMessage:
        return await self.mq.wait_for_event()  # expected type 'MQMessage', got 'Msg' instead

    async def acknowledge_message(self, message: MQMessage):
        await self.mq.acknowledge_message(message)  # unresolved reference 'acknowledge_message' for class 'MessageQueue'

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq.acknowledge_message_in_progress(message)  # unresolved reference 'acknowledge_message_in_progress' for class 'MessageQueue'

    async def watch_for_changes(self, subscriptions: Dict[str, list]):
        await self.kv.watch_for_changes(subscriptions)  # unresolved reference 'watch_for_changes' for class 'KVStore'
