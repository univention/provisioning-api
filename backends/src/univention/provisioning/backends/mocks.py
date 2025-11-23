# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import copy
from typing import Any, Optional

try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock

from nats.aio.msg import Msg
from nats.js.errors import KeyNotFoundError
from nats.js.kv import KeyValue
from test_helpers.mock_data import BASE_KV_OBJ, CONSUMER_HASHED_PASSWORD, MSG, SUBSCRIPTION_NAME

from .key_value_db import BucketName, UpdateConflict
from .nats_kv import NatsKeyValueDB
from .nats_mq import NatsMessageQueue

kv_password = copy.copy(BASE_KV_OBJ)
kv_password.key = SUBSCRIPTION_NAME
kv_password.value = CONSUMER_HASHED_PASSWORD.encode()

kv_sub_info = copy.copy(BASE_KV_OBJ)
kv_sub_info.key = SUBSCRIPTION_NAME
kv_sub_info.value = (
    b'{"name": "0f084f8c-1093-4024-b215-55fe8631ddf6", '
    b'"realms_topics": [{"realm": "udm", "topic": "groups/group"}], '
    b'"request_prefill": true, '
    b'"prefill_queue_status": "done"}'
)
kv_sub_info.revision = 12


class FakeMessageQueue(AsyncMock):
    @classmethod
    async def get(cls):
        return MSG


class FakeKvStore(AsyncMock):
    """Mock of nats.js.kv.KeyValue"""

    def __init__(self, bucket: BucketName, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.bucket = bucket
        if self.bucket == BucketName.credentials:
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


class MockNatsMQAdapter(NatsMessageQueue):
    def __init__(self, server: str, user: str, password: str, max_reconnect_attempts: int = 5, **connect_kwargs):
        super().__init__(server, user, password, max_reconnect_attempts, **connect_kwargs)
        self._nats = AsyncMock()
        self._js = FakeJs()
        self._message_queue = FakeMessageQueue()


class MockNatsKVAdapter(NatsKeyValueDB):
    def __init__(self, server: str, user: str, password: str):
        super().__init__(server, user, password)
        self._nats = AsyncMock()
        self._js = FakeJs()
