# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib

from nats.aio.msg import Msg

from shared.adapters.consumer_mes_adapter import ConsumerMesAdapter
from shared.adapters.consumer_reg_adapter import ConsumerRegAdapter
from shared.adapters.nats_adapter import NatsAdapter
from shared.adapters.udm_adapter import UDMAdapter
from shared.config import settings
from shared.models import FillQueueStatus, Message


class PrefillPort:
    def __init__(self):
        self._udm_adapter = UDMAdapter()
        self._nats_adapter = NatsAdapter()
        self._consumer_reg_adapter = ConsumerRegAdapter()
        self._consumer_mes_adapter = ConsumerMesAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = PrefillPort()
        await port._udm_adapter.connect()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()
        await port._consumer_reg_adapter.connect()
        await port._consumer_mes_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self._udm_adapter.close()
        await self._nats_adapter.close()
        await self._consumer_reg_adapter.close()
        await self._consumer_mes_adapter.close()

    async def subscribe_to_queue(self, subject: str, consumer_name: str):
        await self._nats_adapter.subscribe_to_queue(subject, consumer_name)

    async def wait_for_event(self) -> Msg:
        return await self._nats_adapter.wait_for_event()

    async def get_object_types(self):
        return await self._udm_adapter.get_object_types()

    async def list_objects(self, object_type):
        return await self._udm_adapter.list_objects(object_type)

    async def get_object(self, url):
        return await self._udm_adapter.get_object(url)

    async def update_subscriber_queue_status(
        self, name: str, queue_status: FillQueueStatus
    ) -> None:
        await self._consumer_reg_adapter.update_subscriber_queue_status(
            name, queue_status
        )

    async def create_prefill_message(self, name: str, message: Message):
        await self._consumer_mes_adapter.create_prefill_message(name, message)

    async def create_prefill_stream(self, subscriber_name: str):
        await self._consumer_mes_adapter.create_prefill_stream(subscriber_name)
