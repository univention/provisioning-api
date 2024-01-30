# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from typing import List

import contextlib
import logging

from nats.aio.msg import Msg

from shared.adapters.consumer_reg_adapter import ConsumerRegAdapter
from shared.adapters.nats_adapter import NatsMQAdapter, NatsKVAdapter

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self):
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()
        self._consumer_reg_adapter = ConsumerRegAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port.mq_adapter.connect()
        await port.kv_adapter.connect()
        await port._consumer_reg_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()
        await self._consumer_reg_adapter.close()

    async def send_event_to_consumer_queue(self, subject: str, message):
        await self.mq_adapter.add_message(subject, message)

    async def get_list_value(self, key: str) -> List[str]:
        result = await self.kv_adapter.get_value(key)
        return result.value.decode("utf-8").split(",") if result else []

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.mq_adapter.subscribe_to_queue(subject, deliver_subject)

    async def wait_for_event(self) -> Msg:
        return await self.mq_adapter.wait_for_event()

    async def get_realm_topic_subscribers(self, realm_topic: str) -> list[dict]:
        return await self._consumer_reg_adapter.get_realm_topic_subscribers(realm_topic)
