# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
from typing import Optional

from server.adapters.internal_api_adapter import InternalAPIAdapter
from server.adapters.nats_adapter import NatsMQAdapter
from server.adapters.udm_adapter import UDMAdapter
from univention.provisioning.models import (
    FillQueueStatus,
    Message,
    MQMessage,
    PrefillMessage,
)

from .config import PrefillSettings


class PrefillPort:
    def __init__(self, settings: Optional[PrefillSettings] = None):
        self.settings = settings or PrefillSettings()
        self._udm_adapter = UDMAdapter()
        self.mq_adapter = NatsMQAdapter()
        self._internal_api_adapter = InternalAPIAdapter(self.settings.prefill_username, self.settings.prefill_password)

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = PrefillPort()
        await port._udm_adapter.connect()
        await port.mq_adapter.connect(
            server=port.settings.nats_server,
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
        await self._udm_adapter.close()
        await self.mq_adapter.close()
        await self._internal_api_adapter.close()

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.mq_adapter.subscribe_to_queue(subject, deliver_subject)

    async def wait_for_event(self) -> MQMessage:
        return await self.mq_adapter.wait_for_event()

    async def get_object_types(self):
        return await self._udm_adapter.get_object_types()

    async def list_objects(self, object_type):
        return await self._udm_adapter.list_objects(object_type)

    async def get_object(self, url):
        return await self._udm_adapter.get_object(url)

    async def update_subscription_queue_status(self, name: str, queue_status: FillQueueStatus) -> None:
        await self._internal_api_adapter.update_subscription_queue_status(name, queue_status)

    async def create_prefill_message(self, stream: str, subject: str, message: Message):
        await self.mq_adapter.add_message(stream, subject, message)

    async def add_request_to_prefill_failures(self, stream: str, subject: str, message: PrefillMessage):
        await self.mq_adapter.add_message(stream, subject, message)

    async def create_stream(self, subject: str):
        await self.mq_adapter.ensure_stream(subject)

    async def delete_stream(self, stream_name: str):
        await self.mq_adapter.delete_stream(stream_name)

    async def create_consumer(self, subject: str):
        await self.mq_adapter.ensure_consumer(subject)

    async def acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message(message)

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_in_progress(message)

    async def remove_old_messages_from_prefill_subject(self, stream: str, subject: str):
        await self.mq_adapter.purge_subject_from_messages(stream, subject)
