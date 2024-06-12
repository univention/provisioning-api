# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import Optional
from server.adapters.internal_api_client import InternalAPIClient, AsyncInternalAPIClient
from server.adapters.nats_adapter import (
    Acknowledgements,
    NatsKVStore,
    NatsMessageQueue,
    messagepack_decoder,
)
from univention.provisioning.models import Bucket, Message
from .config import UDMTransformerSettings, get_udm_transformer_settings
from server.adapters.ports import KVStore, MessageQueue


class UDMTransformerPort:  # Not a port in the sense of ports-and-adapters. What role does this class have?
    def __init__(self, settings: Optional[UDMTransformerSettings] = None):
        self.settings = settings or get_udm_transformer_settings()

        self.mq: MessageQueue = NatsMessageQueue()
        self.kv: KVStore = NatsKVStore()
        self._internal_api: InternalAPIClient = AsyncInternalAPIClient(
            self.settings.events_username_udm, self.settings.events_password_udm
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMTransformerPort()
        await port.kv.init(
            [Bucket.cache],
            user=port.settings.nats_user,
            password=port.settings.nats_password,
        )
        await port.mq.connect(
            port.settings.nats_server,
            port.settings.nats_user,
            port.settings.nats_password,
        )
        await port._internal_api.connect()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.kv.close()
        await self._internal_api.close()
        await self.mq.close()

    async def initialize_subscription(self, stream: str, subject: str, durable_name):
        return await self.mq.initialize_subscription(  # unresolved reference 'initialize_subscription' for class 'MessageQueue'
            stream, subject, durable_name
        )

    async def get_message(
        self, timeout: float
    ) -> tuple[Message | None, Acknowledgements | None]:
        return await self.mq.get_one_message(timeout, messagepack_decoder)  # unresolved reference 'get_one_message' for class 'MessageQueue'

    async def retrieve(self, url: str, bucket: Bucket):
        result = await self.kv.get_value(url, bucket)
        return json.loads(result) if result else None  # expected type 'str | bytes | bytearray', got 'Entry' instead

    async def store(self, url: str, new_obj: str, bucket: Bucket):
        await self.kv.put_value(url, new_obj, bucket)

    async def send_event(self, message: Message):
        await self._internal_api.send_event(message)
