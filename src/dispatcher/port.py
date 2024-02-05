# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from typing import List

import contextlib
import logging

from shared.adapters.consumer_registration_adapter import ConsumerRegistrationAdapter
from shared.adapters.nats_adapter import NatsMQAdapter, NatsKVAdapter
from shared.models.queue import MQMessage

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self):
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()
        self._consumer_registration_adapter = ConsumerRegistrationAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.mq_adapter.connect()
        await port.kv_adapter.connect()
        await port._consumer_registration_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()
        await self._consumer_registration_adapter.close()

    async def send_event_to_consumer_queue(self, subject: str, message):
        await self.mq_adapter.add_message(subject, message)

    async def get_list_value(self, key: str) -> List[str]:
        result = await self.kv_adapter.get_value(key)
        return result.value.decode("utf-8").split(",") if result else []

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.mq_adapter.subscribe_to_queue(subject, deliver_subject)

    async def wait_for_event(self) -> MQMessage:
        return await self.mq_adapter.wait_for_event()

    async def get_realm_topic_subscribers(self, realm_topic: str) -> list[dict]:
        return await self._consumer_registration_adapter.get_realm_topic_subscribers(
            realm_topic
        )

    async def acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message(message)

    async def negatively_acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.negatively_acknowledge_message(message)

    async def acknowledge_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_in_progress(message)
