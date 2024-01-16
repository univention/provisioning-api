# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from copy import copy, deepcopy
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from nats.aio.msg import Msg
from nats.js.errors import KeyNotFoundError
from nats.js.kv import KeyValue
from consumer.port import ConsumerPort
from consumer.main import app
from events.port import EventsPort
from shared.adapters.nats_adapter import NatsKVAdapter, NatsMQAdapter
from shared.models import Message
from shared.models.queue import MQMessage

REALM = "udm"
TOPIC = "users/user"
BODY = {"new": {"New": "Object"}, "old": {"Old": "Object"}}
PUBLISHER_NAME = "udm-listener"
REALM_TOPIC = [REALM, TOPIC]
REALMS_TOPICS_STR = f"{REALM}:{TOPIC}"
SUBSCRIBER_NAME = "0f084f8c-1093-4024-b215-55fe8631ddf6"

SUBSCRIBER_INFO = {
    "name": SUBSCRIBER_NAME,
    "realms_topics": [REALMS_TOPICS_STR],
    "fill_queue": True,
    "fill_queue_status": "done",
}
MESSAGE = Message(
    publisher_name=PUBLISHER_NAME,
    ts=datetime(2023, 11, 9, 11, 15, 52, 616061),
    realm=REALM,
    topic=TOPIC,
    body=BODY,
)
MESSAGE_FOR_ONE_SUB = deepcopy(MESSAGE)
MESSAGE_FOR_ONE_SUB.destination = SUBSCRIBER_NAME

FLAT_MESSAGE = {
    "publisher_name": PUBLISHER_NAME,
    "ts": "2023-11-09T11:15:52.616061",
    "realm": REALM,
    "topic": TOPIC,
    "body": BODY,
    "destination": "*",
}
FLAT_MESSAGE_ENCODED = (
    b'{"publisher_name": "udm-listener", "ts": "2023-11-09T11:15:52.616061", "realm": "udm", "topic": "users/user", '
    b'"body": {"new": {"New": "Object"}, "old": {"Old": "Object"}}, "destination": "*"}'
)

FLAT_MESSAGE_FOR_ONE_SUB = deepcopy(FLAT_MESSAGE)
FLAT_MESSAGE_FOR_ONE_SUB["destination"] = SUBSCRIBER_NAME

FLAT_MES_FOR_ONE_SUB_ENCODED = (
    b'{"publisher_name": "udm-listener", "ts": "2023-11-09T11:15:52.616061", "realm": "udm", "topic": "users/user", '
    b'"body": {"new": {"New": "Object"}, "old": {"Old": "Object"}}, '
    b'"destination": "0f084f8c-1093-4024-b215-55fe8631ddf6"}'
)

MSG = Msg(_client="nats", data=json.dumps(FLAT_MESSAGE).encode())
MSG_FOR_ONE_SUB = Msg(
    _client="nats", data=json.dumps(FLAT_MESSAGE_FOR_ONE_SUB).encode()
)

MQMESSAGE = MQMessage(
    subject="",
    reply="",
    data={
        "publisher_name": "udm-listener",
        "ts": "2023-11-09T11:15:52.616061",
        "realm": "udm",
        "topic": "users/user",
        "body": {"new": {"New": "Object"}, "old": {"Old": "Object"}},
        "destination": "*",
    },
    headers=None,
)

BASE_KV_OBJ = KeyValue.Entry(
    "KV_bucket",
    "",
    None,
    None,
    None,
    None,
    None,
)

kv_sub_info = copy(BASE_KV_OBJ)
kv_sub_info.key = f"subscriber:{SUBSCRIBER_NAME}"
kv_sub_info.value = (
    b'{"name": "0f084f8c-1093-4024-b215-55fe8631ddf6", "realms_topics": ["udm:users/user"], "fill_queue": true, '
    b'"fill_queue_status": "done"}'
)

kv_subs = copy(BASE_KV_OBJ)
kv_subs.key = "abc:def"
kv_subs.value = b"0f084f8c-1093-4024-b215-55fe8631ddf6"


class FakeMessageQueue(AsyncMock):
    @classmethod
    async def get(cls):
        return MSG


class FakeJs(AsyncMock):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    Msg.ack = AsyncMock()

    @classmethod
    async def pull_subscribe(cls, subject: str, durable: str, stream: str):
        return cls.sub


class FakeKvStore(AsyncMock):
    @classmethod
    async def get(cls, key: str):
        values = {
            "abc:def": kv_subs,
            "foo:bar": kv_subs,
            f"subscriber:{SUBSCRIBER_NAME}": kv_sub_info,
            "udm:users/user": kv_subs,
        }
        if values.get(key):
            return values.get(key)
        raise KeyNotFoundError


async def consumer_port_fake_dependency() -> ConsumerPort:
    port = ConsumerPort()
    port.mq_adapter = MockMqAdapter()
    port.kv_adapter = MockNatsKVAdapter()
    return port


async def events_port_fake_dependency() -> EventsPort:
    port = EventsPort()
    port.mq_adapter = MockMqAdapter()
    return port


class MockMqAdapter(NatsMQAdapter):
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
        self._kv_store = FakeKvStore()


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def override_dependencies():
    # Override original port
    app.dependency_overrides[
        ConsumerPort.port_dependency
    ] = consumer_port_fake_dependency
    app.dependency_overrides[EventsPort.port_dependency] = events_port_fake_dependency
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
