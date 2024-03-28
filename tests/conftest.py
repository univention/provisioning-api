# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import json
from copy import copy, deepcopy
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
import pytest
from fastapi.security import HTTPBasicCredentials
from nats.aio.msg import Msg
from nats.js.errors import KeyNotFoundError
from nats.js.kv import KeyValue
from tests import set_test_env_vars
from server.adapters.nats_adapter import NatsKVAdapter, NatsMQAdapter
from shared.models.subscription import Bucket
from shared.models import (
    Message,
    MessageProcessingStatusReport,
    MessageProcessingStatus,
    MQMessage,
    PublisherName,
    ProvisioningMessage,
    PrefillMessage,
)

set_test_env_vars()

from server.core.app.config import AppSettings  # noqa: E402
from server.services.port import Port  # noqa: E402
from server.core.app.main import app, internal_app  # noqa: E402

REALM = "udm"
TOPIC = "groups/group"
BODY = {"new": {"New": "Object"}, "old": {"Old": "Object"}}
PUBLISHER_NAME = PublisherName.udm_listener
REALM_TOPIC = [REALM, TOPIC]
REALMS_TOPICS = [(REALM, TOPIC)]
REALMS_TOPICS_STR = f"{REALM}:{TOPIC}"
SUBSCRIPTION_NAME = "0f084f8c-1093-4024-b215-55fe8631ddf6"
REPLY = f"$JS.ACK.stream:{SUBSCRIPTION_NAME}.durable_name:{SUBSCRIPTION_NAME}.1.1.1.1699615014739091916.0"

REPORT = MessageProcessingStatusReport(
    status=MessageProcessingStatus.ok,
    message_seq_num=1,
    publisher_name=PublisherName.udm_listener,
)

CONSUMER_PASSWORD = "password"
CONSUMER_HASHED_PASSWORD = (
    "$2b$12$G56ltBheLThdzppmOX.bcuAdZ.Ffx65oo7Elc.OChmzENtXtA1iSe"
)

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
PROVISIONING_MESSAGE = ProvisioningMessage(
    publisher_name=PUBLISHER_NAME,
    ts=datetime(2023, 11, 9, 11, 15, 52, 616061),
    realm=REALM,
    topic=TOPIC,
    body=BODY,
    sequence_number=1,
    num_delivered=1,
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
    reply=REPLY,
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
    reply=REPLY,
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
    reply=REPLY,
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
    subject="",
    reply=REPLY,
    data=FLAT_MESSAGE,
    headers=None,
    num_delivered=1,
    sequence_number=1,
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
kv_subs.value = b'["0f084f8c-1093-4024-b215-55fe8631ddf6"]'

kv_password = copy(BASE_KV_OBJ)
kv_password.key = SUBSCRIPTION_NAME
kv_password.value = CONSUMER_HASHED_PASSWORD.encode()

CREDENTIALS = HTTPBasicCredentials(username="dev-user", password="dev-password")

SUBSCRIPTIONS = {REALMS_TOPICS_STR: [SUBSCRIPTION_NAME]}


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
    async def pull_subscribe(cls, subject: str, durable: str, stream: str):
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


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(autouse=True)
def override_dependencies():
    # Override original port
    app.dependency_overrides[Port.port_dependency] = port_fake_dependency
    internal_app.dependency_overrides[Port.port_dependency] = port_fake_dependency
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
    internal_app.dependency_overrides.clear()
