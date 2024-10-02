# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any, Optional
from unittest.mock import AsyncMock

from nats.aio.msg import Msg
from nats.js.errors import KeyNotFoundError
from nats.js.kv import KeyValue

from univention.provisioning.adapters.nats_adapter import NatsKVAdapter, NatsMQAdapter, UpdateConflict
from univention.provisioning.models.constants import Bucket
from univention.provisioning.rest.config import AppSettings
from univention.provisioning.services.port import Port

from .mock_data import MSG, SUBSCRIPTION_NAME, kv_password, kv_sub_info


class FakeMessageQueue(AsyncMock):
    @classmethod
    async def get(cls):
        return MSG


class FakeKvStore(AsyncMock):
    """Mock of nats.js.kv.KeyValue"""

    def __init__(self, bucket: Bucket, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.bucket = bucket
        if self.bucket == Bucket.credentials:
            self._values = {SUBSCRIPTION_NAME: kv_password}
        else:
            self._values = {SUBSCRIPTION_NAME: kv_sub_info}

    async def get(self, key: str, revision: Optional[int] = None) -> KeyValue.Entry:
        if self._values.get(key):
            return self._values.get(key)
        raise KeyNotFoundError

    async def keys(self):
        return list(self._values.keys())

    async def put(self, key: str, value: bytes) -> int:
        self._values[key] = value
        return 43

    async def update(self, key: str, value: bytes, last: Optional[int] = None) -> int:
        value = self._values.get(key)
        if last is not None and value.revision != last:
            raise UpdateConflict(f"Stored value has revision {value.revision}. Passed revision {last} doesn't match.")
        self._values[key] = value
        return 43


class FakeJs(AsyncMock):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    Msg.ack = AsyncMock()

    @classmethod
    async def pull_subscribe(cls, subject: str, durable: str, stream: str, config=None):
        return cls.sub

    @classmethod
    async def key_value(cls, bucket: str):
        return FakeKvStore(bucket)


async def port_fake_dependency() -> Port:
    port = Port(AppSettings(nats_user="api", nats_password="apipass"))
    port.mq_adapter = MockNatsMQAdapter()
    port.kv_adapter = MockNatsKVAdapter()
    return port


class MockNatsMQAdapter(NatsMQAdapter):
    def __init__(self):
        super().__init__()
        self._nats = AsyncMock()
        self._js = FakeJs()
        self._message_queue = FakeMessageQueue()


class MockNatsKVAdapter(NatsKVAdapter):
    def __init__(self):
        super().__init__()
        self._nats = AsyncMock()
        self._js = FakeJs()
