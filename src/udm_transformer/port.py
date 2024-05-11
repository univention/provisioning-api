# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import Callable, Optional
from server.adapters.internal_api_adapter import InternalAPIAdapter
from server.adapters.nats_adapter import NatsKVAdapter, NatsMQAdapter
from shared.models import Bucket, Message
from .config import UDMTransformerSettings, get_udm_transformer_settings


class UDMMessagingPort:
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
        port = UDMMessagingPort()
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

    async def initialize_subscription(
        self, stream: str, subject: str, consumer_name: str
    ):
        return await self.mq_adapter.initialize_subscription(
            stream,
            subject,
            consumer_name,
        )

    async def get_msgpack_message(
        self, timeout: float
    ) -> tuple[Message | None, Callable | None]:
        return await self.mq_adapter.get_msgpack_message(timeout)

    async def retrieve(self, url: str, bucket: Bucket):
        result = await self.kv_adapter.get_value(url, bucket)
        return json.loads(result) if result else None

    async def store(self, url: str, new_obj: str, bucket: Bucket):
        await self.kv_adapter.put_value(url, new_obj, bucket)

    async def send_event(self, message: Message):
        await self._internal_api_adapter.send_event(message)
