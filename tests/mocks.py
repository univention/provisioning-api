# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any
from unittest.mock import AsyncMock

from nats.aio.msg import Msg
from nats.js.errors import KeyNotFoundError

from server.adapters.nats_adapter import NatsKVAdapter, NatsMQAdapter
from server.core.app.config import AppSettings
from server.services.port import Port
from univention.provisioning.models.subscription import Bucket

from .mock_data import MSG, SUBSCRIPTION_NAME, kv_password, kv_sub_info, kv_subs


class FakeMessageQueue(AsyncMock):
    @classmethod
    async def get(cls):
        return MSG


class FakeKvStore(AsyncMock):
    def __init__(self, bucket: Bucket, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.bucket = bucket

    async def get(self, key: str):
        if self.bucket == Bucket.credentials:
            values = {SUBSCRIPTION_NAME: kv_password}
        else:
            values = {
                "abc:def": kv_subs,
                "foo:bar": kv_subs,
                SUBSCRIPTION_NAME: kv_sub_info,
                "realm:topic.udm:groups/group": kv_subs,
            }
        if values.get(key):
            return values.get(key)
        raise KeyNotFoundError

    @classmethod
    async def keys(cls):
        return [SUBSCRIPTION_NAME]


class FakeJs(AsyncMock):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    Msg.ack = AsyncMock()

    @classmethod
    async def pull_subscribe(cls, subject: str, durable: str, stream: str, config):
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
