# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from copy import copy, deepcopy
from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from fastapi.security import HTTPBasicCredentials
from nats.aio.msg import Msg
from nats.js.errors import KeyNotFoundError
from nats.js.kv import KeyValue

from admin.port import AdminPort
from consumer.port import ConsumerPort
from consumer.main import app
from events.port import EventsPort
from shared.adapters.nats_adapter import NatsKVAdapter, NatsMQAdapter
from shared.models import Message
from shared.models.queue import MQMessage
from shared.models.queue import PrefillMessage

REALM = "udm"
TOPIC = "groups/group"
BODY = {"new": {"New": "Object"}, "old": {"Old": "Object"}}
PUBLISHER_NAME = "udm-listener"
REALM_TOPIC = [REALM, TOPIC]
REALMS_TOPICS = [[REALM, TOPIC]]
REALMS_TOPICS_STR = f"{REALM}:{TOPIC}"
SUBSCRIPTION_NAME = "0f084f8c-1093-4024-b215-55fe8631ddf6"

SUBSCRIPTION_INFO = {
    "name": SUBSCRIPTION_NAME,
    "realms_topics": [REALMS_TOPICS_STR],
    "request_prefill": True,
    "prefill_queue_status": "done",
}
MESSAGE = Message(
    publisher_name=PUBLISHER_NAME,
    ts=datetime(2023, 11, 9, 11, 15, 52, 616061),
    realm=REALM,
    topic=TOPIC,
    body=BODY,
)
PREFILL_MESSAGE = PrefillMessage(
    publisher_name=PUBLISHER_NAME,
    ts=datetime(2023, 11, 9, 11, 15, 52, 616061),
    realms_topics=REALMS_TOPICS,
    subscription_name=SUBSCRIPTION_NAME,
)

FLAT_BASE_MESSAGE = {
    "publisher_name": PUBLISHER_NAME,
    "ts": "2023-11-09T11:15:52.616061",
}
FLAT_MESSAGE = deepcopy(FLAT_BASE_MESSAGE)
FLAT_MESSAGE["body"] = BODY
FLAT_MESSAGE["realm"] = REALM
FLAT_MESSAGE["topic"] = TOPIC

FLAT_PREFILL_MESSAGE = deepcopy(FLAT_BASE_MESSAGE)
FLAT_PREFILL_MESSAGE["subscription_name"] = SUBSCRIPTION_NAME
FLAT_PREFILL_MESSAGE["realms_topics"] = REALMS_TOPICS

MSG = Msg(
    _client="nats",
    data=json.dumps(FLAT_MESSAGE).encode(),
    _metadata=Msg.Metadata(
        sequence=Msg.Metadata.SequencePair(consumer=5, stream=5),
        num_pending=0,
        num_delivered=1,
        timestamp=datetime(2023, 11, 9, 11, 15, 52, 616061),
        stream=f"stream:{SUBSCRIPTION_NAME}",
        consumer=SUBSCRIPTION_NAME,
        domain=None,
    ),
)
MSG_PREFILL = Msg(
    _client="nats",
    data=json.dumps(FLAT_PREFILL_MESSAGE).encode(),
    _metadata=Msg.Metadata(
        sequence=Msg.Metadata.SequencePair(consumer=5, stream=5),
        num_pending=0,
        num_delivered=1,
        timestamp=datetime(2023, 11, 9, 11, 15, 52, 616061),
        stream="stream:prefill",
        consumer="prefill-service",
        domain=None,
    ),
)
MSG_PREFILL_REDELIVERED = Msg(
    _client="nats",
    data=json.dumps(FLAT_PREFILL_MESSAGE).encode(),
    _metadata=Msg.Metadata(
        sequence=Msg.Metadata.SequencePair(consumer=5, stream=5),
        num_pending=0,
        num_delivered=4,
        timestamp=datetime(2023, 11, 9, 11, 15, 52, 616061),
        stream="stream:prefill",
        consumer="prefill-service",
        domain=None,
    ),
)

MQMESSAGE = MQMessage(
    subject="", reply="", data=FLAT_MESSAGE, headers=None, num_delivered=1
)

MQMESSAGE_PREFILL = deepcopy(MQMESSAGE)
MQMESSAGE_PREFILL.data = FLAT_PREFILL_MESSAGE

MQMESSAGE_PREFILL_REDELIVERED = deepcopy(MQMESSAGE_PREFILL)
MQMESSAGE_PREFILL_REDELIVERED.num_delivered = 4

FLAT_MESSAGE_ENCODED = (
    b'{"publisher_name": "udm-listener", "ts": "2023-11-09T11:15:52.616061", "realm": "udm", "topic": "groups/group", '
    b'"body": {"new": {"New": "Object"}, "old": {"Old": "Object"}}}'
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
kv_sub_info.key = SUBSCRIPTION_NAME
kv_sub_info.value = (
    b'{"name": "0f084f8c-1093-4024-b215-55fe8631ddf6", "realms_topics": ["udm:groups/group"], "request_prefill": true, '
    b'"prefill_queue_status": "done"}'
)

kv_subs = copy(BASE_KV_OBJ)
kv_subs.key = "abc:def"
kv_subs.value = b"0f084f8c-1093-4024-b215-55fe8631ddf6"

CREDENTIALS = HTTPBasicCredentials(username="dev-user", password="dev-password")


class FakeMessageQueue(AsyncMock):
    @classmethod
    async def get(cls):
        return MSG


class FakeKvStore(AsyncMock):
    @classmethod
    async def get(cls, key: str):
        values = {
            "abc:def": kv_subs,
            "foo:bar": kv_subs,
            SUBSCRIPTION_NAME: kv_sub_info,
            "udm:groups/group": kv_subs,
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
    async def pull_subscribe(cls, subject: str, durable: str, stream: str):
        return cls.sub

    @classmethod
    async def key_value(cls, bucket: str):
        return FakeKvStore()


async def consumer_port_fake_dependency() -> ConsumerPort:
    port = ConsumerPort()
    port.mq_adapter = MockNatsMQAdapter()
    port.kv_adapter = MockNatsKVAdapter()
    return port


async def events_port_fake_dependency() -> EventsPort:
    port = EventsPort()
    port.mq_adapter = MockNatsMQAdapter()
    return port


async def admin_port_fake_dependency() -> AdminPort:
    port = AdminPort()
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


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def override_dependencies():
    # Override original port
    app.dependency_overrides = {
        ConsumerPort.port_dependency: consumer_port_fake_dependency,
        EventsPort.port_dependency: events_port_fake_dependency,
        AdminPort.port_dependency: admin_port_fake_dependency,
    }
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
