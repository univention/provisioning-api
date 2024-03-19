# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
from shared.adapters.internal_api_adapter import InternalAPIAdapter
import logging
from typing import List, Optional

from shared.adapters.nats_adapter import NatsMQAdapter
from shared.models import Message, MQMessage

from .config import DispatcherSettings

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        self.settings = settings or DispatcherSettings()
        self.mq_adapter = NatsMQAdapter()
        self._internal_api_adapter = InternalAPIAdapter(
            self.settings.dispatcher_username, self.settings.dispatcher_password
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.mq_adapter.connect(
            user=port.settings.nats_user,
            password=port.settings.nats_password,
            max_reconnect_attempts=port.settings.max_reconnect_attempts,
        )
        await port._internal_api_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self._internal_api_adapter.close()

    async def send_message_to_subscription(self, name: str, message: Message):
        await self._internal_api_adapter.send_message(name, message)

    async def subscribe_to_queue(self, stream_subject: str, deliver_subject: str):
        await self.mq_adapter.subscribe_to_queue(stream_subject, deliver_subject)

    async def wait_for_event(self) -> MQMessage:
        return await self.mq_adapter.wait_for_event()

    async def get_realm_topic_subscriptions(self, realm_topic: str) -> List[str]:
        return await self._internal_api_adapter.get_realm_topic_subscriptions(
            realm_topic
        )

    async def acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message(message)

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_in_progress(message)

    async def create_stream(self, subject: str):
        await self.mq_adapter.create_stream(subject)

    async def create_consumer(self, subject: str):
        await self.mq_adapter.create_consumer(subject)

    async def add_event_to_dispatcher_failures(self, queue_name: str, message: Message):
        await self.mq_adapter.add_message(queue_name, message)
