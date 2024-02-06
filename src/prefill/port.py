# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib

from shared.adapters.consumer_messages_adapter import ConsumerMessagesAdapter
from shared.adapters.consumer_registration_adapter import ConsumerRegistrationAdapter
from shared.adapters.nats_adapter import NatsMQAdapter
from shared.adapters.udm_adapter import UDMAdapter
from shared.models import FillQueueStatus, Message
from shared.models.queue import PrefillMessage, MQMessage


class PrefillPort:
    def __init__(self):
        self._udm_adapter = UDMAdapter()
        self.mq_adapter = NatsMQAdapter()
        self._consumer_registration_adapter = ConsumerRegistrationAdapter()
        self._consumer_messages_adapter = ConsumerMessagesAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = PrefillPort()
        await port._udm_adapter.connect()
        await port.mq_adapter.connect()
        await port._consumer_registration_adapter.connect()
        await port._consumer_messages_adapter.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self._udm_adapter.close()
        await self.mq_adapter.close()
        await self._consumer_registration_adapter.close()
        await self._consumer_messages_adapter.close()

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

    async def update_subscriber_queue_status(
        self, name: str, queue_status: FillQueueStatus
    ) -> None:
        await self._consumer_registration_adapter.update_subscriber_queue_status(
            name, queue_status
        )

    async def create_prefill_message(self, name: str, message: Message):
        await self._consumer_messages_adapter.create_prefill_message(name, message)

    async def create_prefill_stream(self, subscriber_name: str):
        await self._consumer_messages_adapter.create_prefill_stream(subscriber_name)

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
