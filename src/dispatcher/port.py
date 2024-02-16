# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from typing import List

import contextlib
import logging

from shared.adapters.internal_api_adapter import InternalAPIAdapter
from shared.adapters.nats_adapter import NatsMQAdapter
from shared.config import settings
from shared.models.queue import MQMessage, Message

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self):
        self.mq_adapter = NatsMQAdapter()
        self._internal_api_adapter = InternalAPIAdapter(
            settings.dispatcher_username, settings.dispatcher_password
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.mq_adapter.connect()
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

    async def acknowledge_message_negatively(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_negatively(message)

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_in_progress(message)
