# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib

from nats.aio.msg import Msg

from shared.adapters.nats_adapter import NatsAdapter
from shared.adapters.udm_adapter import UDMAdapter
from shared.config import settings


class PrefillPort:
    def __init__(self):
        self._udm_adapter = UDMAdapter()
        self._nats_adapter = NatsAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = PrefillPort()
        await port._udm_adapter.connect()
        await port._nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port._nats_adapter.create_kv_store()

        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self._udm_adapter.close()
        await self._nats_adapter.close()

    async def subscribe_to_queue(self, subject: str):
        await self._nats_adapter.subscribe_to_queue(subject)

    async def wait_for_event(self) -> Msg:
        return await self._nats_adapter.wait_for_event()

    async def get_object_types(self):
        return self._udm_adapter.get_object_types()

    async def list_objects(self, object_type):
        return self._udm_adapter.list_objects(object_type)

    async def get_object(self, url):
        return self._udm_adapter.get_object(url)
