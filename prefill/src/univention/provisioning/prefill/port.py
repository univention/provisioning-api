# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
from typing import Optional, Tuple

from univention.provisioning.backends.message_queue import Acknowledgements
from univention.provisioning.backends.nats_mq import NatsMessageQueue
from univention.provisioning.models.message import BaseMessage, Message, MQMessage
from univention.provisioning.models.subscription import FillQueueStatus

from .config import PrefillSettings, prefill_settings
from .udm_adapter import UDMAdapter
from .update_sub_q_status_adapter_rest_api import SubscriptionsRestApiAdapter
from .update_sub_q_status_port import UpdateSubscriptionsQueueStatusPort


class PrefillPort:
    def __init__(self, settings: Optional[PrefillSettings] = None):
        self.settings = settings or prefill_settings()
        self.mq_adapter = NatsMessageQueue(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )
        self._update_sub_q_status: UpdateSubscriptionsQueueStatusPort = SubscriptionsRestApiAdapter(
            self.settings.provisioning_api_url, self.settings.prefill_username, self.settings.prefill_password
        )
        self._udm_adapter = UDMAdapter(self.settings.udm_url, self.settings.udm_username, self.settings.udm_password)

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = PrefillPort()
        await port._udm_adapter.connect()
        await port.mq_adapter.connect()
        await port._update_sub_q_status.connect()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self._udm_adapter.close()
        await self.mq_adapter.close()
        await self._update_sub_q_status.close()

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str | None) -> None:
        await self.mq_adapter.initialize_subscription(stream, manual_delete, subject)

    async def get_one_message(
        self,
    ) -> Tuple[MQMessage, Acknowledgements]:
        return await self.mq_adapter.get_one_message()

    async def get_object_types(self):
        return await self._udm_adapter.get_object_types()

    async def list_objects(self, object_type):
        return await self._udm_adapter.list_objects(object_type)

    async def get_object(self, url):
        return await self._udm_adapter.get_object(url)

    async def update_subscription_queue_status(self, name: str, queue_status: FillQueueStatus) -> None:
        await self._update_sub_q_status.update_subscription_queue_status(name, queue_status)

    async def create_prefill_message(self, stream: str, subject: str, message: Message):
        await self.mq_adapter.add_message(stream, subject, message)

    async def add_request_to_prefill_failures(self, stream: str, subject: str, message: BaseMessage):
        await self.mq_adapter.add_message(stream, subject, message)

    async def ensure_stream(self, subject: str, manual_delete: bool):
        await self.mq_adapter.ensure_stream(subject, manual_delete)

    async def delete_stream(self, stream_name: str):
        await self.mq_adapter.delete_stream(stream_name)

    async def ensure_consumer(self, subject: str):
        await self.mq_adapter.ensure_consumer(subject)

    async def acknowledge_message(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message(message)

    async def acknowledge_message_in_progress(self, message: MQMessage):
        await self.mq_adapter.acknowledge_message_in_progress(message)

    async def remove_old_messages_from_prefill_subject(self, stream: str, subject: str):
        await self.mq_adapter.purge_subject_from_messages(stream, subject)
