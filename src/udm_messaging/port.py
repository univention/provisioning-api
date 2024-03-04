# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import Optional
from shared.adapters.internal_api_adapter import InternalAPIAdapter
from shared.adapters.nats_adapter import NatsKVAdapter
from shared.models import Bucket, Message
from .config import UdmMessagingSettings


class UDMMessagingPort:
    def __init__(self, settings: Optional[UdmMessagingSettings] = None):
        self.settings = settings or UdmMessagingSettings()
        self.kv_adapter = NatsKVAdapter()
        self._internal_api_adapter = InternalAPIAdapter(
            self.settings.udm_listener_username, self.settings.udm_listener_password
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
        await port._internal_api_adapter.connect()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.kv_adapter.close()
        await self._internal_api_adapter.close()

    async def retrieve(self, url: str, bucket: Bucket):
        result = await self.kv_adapter.get_value(url, bucket)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def store(self, url: str, new_obj: str, bucket: Bucket):
        await self.kv_adapter.put_value(url, new_obj, bucket)

    async def send_event(self, message: Message):
        await self._internal_api_adapter.send_event(message)
