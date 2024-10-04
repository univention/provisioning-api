# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import Any, Optional

import msgpack

from univention.provisioning.backends import key_value_store, message_queue
from univention.provisioning.backends.message_queue import Acknowledgements
from univention.provisioning.models.constants import Bucket
from univention.provisioning.models.message import Message, MQMessage

from .config import UDMTransformerSettings, udm_transformer_settings
from .send_event_adapter_rest_api import SubscriptionsRestApiAdapter
from .send_event_port import SendEventPort


def messagepack_decoder(data: bytes) -> Any:
    return msgpack.unpackb(data)


class UDMTransformerPort:
    def __init__(self, settings: Optional[UDMTransformerSettings] = None):
        self.settings = settings or udm_transformer_settings()

        self.mq_adapter = message_queue(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
        )
        self.kv_adapter = key_value_store(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
        )
        self._send_event: SendEventPort = SubscriptionsRestApiAdapter(
            self.settings.provisioning_api_url, self.settings.events_username_udm, self.settings.events_password_udm
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMTransformerPort()
        await port.connect()
        try:
            yield port
        finally:
            await port.close()

    async def connect(self):
        await self.mq_adapter.connect()
        await self.kv_adapter.init(buckets=[Bucket.cache])
        await self._send_event.connect()

    async def close(self):
        await self.kv_adapter.close()
        await self._send_event.close()
        await self.mq_adapter.close()

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str):
        return await self.mq_adapter.initialize_subscription(stream, manual_delete, subject)

    async def get_one_message(self, timeout: float) -> tuple[MQMessage, Acknowledgements]:
        return await self.mq_adapter.get_one_message(timeout=timeout, binary_decoder=messagepack_decoder)

    async def retrieve(self, url: str, bucket: Bucket) -> dict:
        result = await self.kv_adapter.get_value(url, bucket)
        return json.loads(result) if result else {}

    async def store(self, url: str, new_obj: str, bucket: Bucket):
        await self.kv_adapter.put_value(url, new_obj, bucket)

    async def send_event(self, message: Message):
        await self._send_event.send_event(message)
