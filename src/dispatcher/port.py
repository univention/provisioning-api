# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from typing import List

import contextlib
import logging

from shared.adapters.consumer_messages_adapter import ConsumerMessagesAdapter
from shared.adapters.consumer_registration_adapter import ConsumerRegistrationAdapter
from shared.adapters.nats_adapter import NatsMQAdapter, NatsKVAdapter
from shared.models.queue import MQMessage, Message

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self):
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()
        self._consumer_registration_adapter = ConsumerRegistrationAdapter()
        self._consumer_messages_adapter = ConsumerMessagesAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.mq_adapter.connect()
        await port.kv_adapter.connect()
        await port._consumer_registration_adapter.connect()
        await port._consumer_messages_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()
        await self._consumer_registration_adapter.close()
        await self._consumer_messages_adapter.close()

    async def send_message_to_subscription(self, name: str, message: Message):
        await self._consumer_messages_adapter.send_message(name, message)

    async def get_list_value(self, key: str) -> List[str]:
        result = await self.kv_adapter.get_value(key)
        return result.value.decode("utf-8").split(",") if result else []

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.mq_adapter.subscribe_to_queue(subject, deliver_subject)

    async def wait_for_event(self) -> MQMessage:
        return await self.mq_adapter.wait_for_event()

    async def get_realm_topic_subscriptions(self, realm_topic: str) -> List[str]:
        return await self._consumer_registration_adapter.get_realm_topic_subscriptions(
            realm_topic
        )

    async def acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message(message)

    async def acknowledge_message_negatively(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_negatively(message)

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_in_progress(message)
