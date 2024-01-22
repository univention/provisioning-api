# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import logging

from nats.aio.msg import Msg

from shared.adapters.consumer_reg_adapter import ConsumerRegAdapter
from shared.adapters.nats_adapter import NatsAdapter
from shared.config import settings
from shared.models.queue import Message

logger = logging.getLogger(__name__)


class DispatcherPort:
    def __init__(self):
        self._nats_adapter = NatsAdapter()
        self._consumer_reg_adapter = ConsumerRegAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = DispatcherPort()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()
        await port._consumer_reg_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self._nats_adapter.close()
        await self._consumer_reg_adapter.close()

    async def send_event_to_consumer_queue(self, subject: str, message: Message):
        await self._nats_adapter.add_message(subject, message)

    async def subscribe_to_queue(self, subject: str, consumer_name: str):
        await self._nats_adapter.subscribe_to_queue(subject, consumer_name)

    async def wait_for_event(self) -> Msg:
        return await self._nats_adapter.wait_for_event()

    async def get_realm_topic_subscribers(self, realm_topic: str) -> list[dict]:
        return await self._consumer_reg_adapter.get_realm_topic_subscribers(realm_topic)
