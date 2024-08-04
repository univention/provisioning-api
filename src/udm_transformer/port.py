# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import Optional

from server.adapters.internal_api_adapter import InternalAPIAdapter
from server.adapters.nats_adapter import (
    Acknowledgements,
    NatsKVAdapter,
    NatsMQAdapter,
    messagepack_decoder,
)
from univention.provisioning.models import Bucket, Message
from univention.provisioning.models.queue import MQMessage

from .config import UDMTransformerSettings, get_udm_transformer_settings


class UDMTransformerPort:
    def __init__(self, settings: Optional[UDMTransformerSettings] = None):
        self.settings = settings or get_udm_transformer_settings()

        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()
        self._internal_api_adapter = InternalAPIAdapter(
            self.settings.events_username_udm, self.settings.events_password_udm
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMTransformerPort()
        await port.kv_adapter.init(
            [Bucket.cache],
            user=port.settings.nats_user,
            password=port.settings.nats_password,
        )
        await port.mq_adapter.connect(
            port.settings.nats_server,
            port.settings.nats_user,
            port.settings.nats_password,
        )
        await port._internal_api_adapter.connect()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.kv_adapter.close()
        await self._internal_api_adapter.close()
        await self.mq_adapter.close()

    async def initialize_subscription(self, stream: str, subject: str):
        return await self.mq_adapter.initialize_subscription(stream, subject)

    async def get_one_message(self, timeout: float) -> tuple[MQMessage, Acknowledgements]:
        return await self.mq_adapter.get_one_message(timeout=timeout, binary_decoder=messagepack_decoder)

    async def retrieve(self, url: str, bucket: Bucket):
        result = await self.kv_adapter.get_value(url, bucket)
        return json.loads(result) if result else None

    async def store(self, url: str, new_obj: str, bucket: Bucket):
        await self.kv_adapter.put_value(url, new_obj, bucket)

    async def send_event(self, message: Message):
        await self._internal_api_adapter.send_event(message)
