# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json


from shared.adapters.nats_adapter import NatsKVAdapter
from shared.adapters.event_adapter import EventAdapter

from shared.models import Message
from shared.models.subscription import Bucket


class UDMMessagingPort:
    def __init__(self):
        self.kv_adapter = NatsKVAdapter()
        self._event_adapter = EventAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMMessagingPort()
        await port.kv_adapter.init([Bucket.cache])
        await port._event_adapter.connect()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.kv_adapter.close()
        await self._event_adapter.close()

    async def retrieve(self, url: str, bucket: Bucket):
        result = await self.kv_adapter.get_value(url, bucket)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def store(self, url: str, new_obj: str, bucket: Bucket):
        await self.kv_adapter.put_value(url, new_obj, bucket)

    async def send_event(self, message: Message):
        await self._event_adapter.send_event(message)
