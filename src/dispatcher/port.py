# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from typing import List

import contextlib
import logging
from typing import Optional

from nats.aio.msg import Msg

from shared.adapters.consumer_reg_adapter import ConsumerRegAdapter
from shared.adapters.event_adapter import EventAdapter
from shared.models.queue import Message
from shared.adapters.nats_adapter import NatsMQAdapter, NatsKVAdapter
from shared.models.queue import MQMessage

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self):
        self.message_queue = NatsMQAdapter()
        self.kv_store = NatsKVAdapter()
        self._consumer_reg_adapter = ConsumerRegAdapter()
        self._event_adapter = EventAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.message_queue.connect()
        await port.kv_store.connect()
        await port._consumer_reg_adapter.connect()
        await port._event_adapter.connect()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.message_queue.close()
        await self.kv_store.close()
        await self._consumer_reg_adapter.close()
        await self._event_adapter.close()

    async def retrieve_event_from_queue(self, subject, timeout, pop) -> List[MQMessage]:
        return await self.message_queue.get_messages(subject, timeout, 1, pop)

    async def send_event_to_consumer_queue(self, subject: str, message):
        await self.message_queue.add_message(subject, message)

    async def get_list_value(self, key: str) -> List[str]:
        result = await self.kv_store.get_value(key)
        return result.value.decode("utf-8").split(",") if result else []

    async def subscribe_to_queue(self, subject: str):
        await self.message_queue.subscribe_to_queue(subject)

    async def wait_for_event(self) -> Msg:
        return await self.message_queue.wait_for_event()

    async def get_subscriber(self, name: str) -> Optional[dict]:
        return await self._consumer_reg_adapter.get_subscriber(name)

    async def get_realm_topic_subscribers(self, realm_topic: str) -> list[dict]:
        return await self._consumer_reg_adapter.get_realm_topic_subscribers(realm_topic)

    async def send_event_to_incoming_queue(self, message: Message):
        await self._event_adapter.send_event(message)
