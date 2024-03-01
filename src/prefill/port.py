# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
from typing import Optional
from shared.adapters.internal_api_adapter import InternalAPIAdapter
from shared.adapters.nats_adapter import NatsMQAdapter
from shared.adapters.udm_adapter import UDMAdapter
from shared.models import FillQueueStatus, Message, PrefillMessage, MQMessage
from .config import PrefillSettings


class PrefillPort:
    def __init__(self, settings: Optional[PrefillSettings] = None):
        self.settings = settings or PrefillSettings()
        self._udm_adapter = UDMAdapter()
        self.mq_adapter = NatsMQAdapter()
        self._internal_api_adapter = InternalAPIAdapter(
            self.settings.username, self.settings.password
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = PrefillPort()
        await port._udm_adapter.connect()
        await port.mq_adapter.connect(
            user=port.settings.nats_user, password=port.settings.nats_password
        )
        await port._internal_api_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self._udm_adapter.close()
        await self.mq_adapter.close()
        await self._internal_api_adapter.close()

    async def subscribe_to_queue(self, stream_subject: str, deliver_subject: str):
        await self.mq_adapter.subscribe_to_queue(stream_subject, deliver_subject)

    async def wait_for_event(self) -> MQMessage:
        return await self.mq_adapter.wait_for_event()

    async def get_object_types(self):
        return await self._udm_adapter.get_object_types()

    async def list_objects(self, object_type):
        return await self._udm_adapter.list_objects(object_type)

    async def get_object(self, url):
        return await self._udm_adapter.get_object(url)

    async def update_subscription_queue_status(
        self, name: str, queue_status: FillQueueStatus
    ) -> None:
        await self._internal_api_adapter.update_subscription_queue_status(
            name, queue_status
        )

    async def create_prefill_message(self, name: str, message: Message):
        await self._internal_api_adapter.create_prefill_message(name, message)

    async def create_prefill_stream(self, subscription_name: str):
        await self._internal_api_adapter.create_prefill_stream(subscription_name)

    async def add_request_to_prefill_failures(
        self, queue_name: str, message: PrefillMessage
    ):
        await self.mq_adapter.add_message(queue_name, message)

    async def create_stream(self, subject: str):
        await self.mq_adapter.create_stream(subject)

    async def create_consumer(self, subject: str):
        await self.mq_adapter.create_consumer(subject)

    async def acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message(message)

    async def acknowledge_message_negatively(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_negatively(message)

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_in_progress(message)
