# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import Optional

from univention.provisioning.adapters.internal_api_adapter import InternalAPIAdapter
from univention.provisioning.adapters.nats_adapter import (
    Acknowledgements,
    NatsKVAdapter,
    NatsMQAdapter,
    messagepack_decoder,
)
from univention.provisioning.models.constants import Bucket
from univention.provisioning.models.message import Message, MQMessage

from .config import UDMTransformerSettings, udm_transformer_settings


class UDMTransformerPort:
    def __init__(self, settings: Optional[UDMTransformerSettings] = None):
        self.settings = settings or udm_transformer_settings()

        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()
        self._internal_api_adapter = InternalAPIAdapter(
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
        await self.mq_adapter.connect(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
        )
        await self.kv_adapter.init(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            buckets=[Bucket.cache],
        )
        await self._internal_api_adapter.connect()

    async def close(self):
        await self.kv_adapter.close()
        await self._internal_api_adapter.close()
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
        await self._internal_api_adapter.send_event(message)
