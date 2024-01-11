# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json

from shared.adapters.nats_adapter import NatsAdapter
from shared.adapters.event_adapter import EventAdapter

from shared.config import settings
from shared.models import Message


class UDMMessagingPort:
    def __init__(self):
        self._nats_adapter = NatsAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = UDMMessagingPort()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()
        yield port

    async def retrieve(self, url: str):
        result = await self._nats_adapter.get_value(url)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def store(self, url: str, new_obj: str):
        await self._nats_adapter.put_value(url, new_obj)

    @staticmethod
    async def send_event(message: Message):
        async with EventAdapter(
            settings.event_url, settings.event_username, settings.event_password
        ) as adapter:
            await adapter.send_event(message)
