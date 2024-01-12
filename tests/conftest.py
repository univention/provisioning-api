# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from copy import copy
from datetime import datetime
from typing import Union
from unittest.mock import AsyncMock

import pytest
from fakeredis import aioredis
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig
from nats.js.kv import KeyValue
from redis._parsers.helpers import (
    parse_xread_resp3,
    string_keys_to_dict,
    bool_ok,
    parse_command_resp3,
    parse_sentinel_state_resp3,
    parse_sentinel_masters_resp3,
    parse_sentinel_slaves_and_sentinels_resp3,
)
from redis.utils import str_if_bytes
from consumer.port import ConsumerPort
from consumer.main import app
from events.port import EventsPort
from shared.models import Message

REALM = "udm"
TOPIC = "users/user"
BODY = {"new": {"New": "Object"}, "old": {"Old": "Object"}}
PUBLISHER_NAME = "udm-listener"
REALM_TOPIC = [REALM, TOPIC]
REALMS_TOPICS = [f"{REALM}:{TOPIC}"]
SUBSCRIBER_NAME = "0f084f8c-1093-4024-b215-55fe8631ddf6"

SUBSCRIBER_INFO = {
    "name": SUBSCRIBER_NAME,
    "realms_topics": REALMS_TOPICS,
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
FLAT_MESSAGE = {
    "publisher_name": PUBLISHER_NAME,
    "ts": "2023-11-09T11:15:52.616061",
    "realm": REALM,
    "topic": TOPIC,
    "body": BODY,
    "destination": "*",
}

MSG = Msg(_client="nats", data=json.dumps(FLAT_MESSAGE).encode())

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


async def fake_redis():
    connection = aioredis.FakeRedis(decode_responses=True, protocol=2)
    connection.response_callbacks.update(
        {
            # Because fakeredis does not support RESP3 protocol, we need to manually patch some
            # responses of stream commands. Here is a list of operations we might need in the future:
            # ZRANGE ZINTER ZPOPMAX ZPOPMIN ZRANGEBYSCORE ZREVRANGE ZREVRANGEBYSCORE ZUNION HGETALL XREADGROUP"
            **string_keys_to_dict("XREAD XREADGROUP", parse_xread_resp3),
            "ACL LOG": lambda r: [
                {str_if_bytes(key): str_if_bytes(value) for key, value in x.items()}
                for x in r
            ]
            if isinstance(r, list)
            else bool_ok(r),
            "COMMAND": parse_command_resp3,
            "CONFIG GET": lambda r: {
                str_if_bytes(key)
                if key is not None
                else None: str_if_bytes(value)
                if value is not None
                else None
                for key, value in r.items()
            },
            "MEMORY STATS": lambda r: {
                str_if_bytes(key): value for key, value in r.items()
            },
            "SENTINEL MASTER": parse_sentinel_state_resp3,
            "SENTINEL MASTERS": parse_sentinel_masters_resp3,
            "SENTINEL SENTINELS": parse_sentinel_slaves_and_sentinels_resp3,
            "SENTINEL SLAVES": parse_sentinel_slaves_and_sentinels_resp3,
            "STRALGO": lambda r, **options: {
                str_if_bytes(key): str_if_bytes(value) for key, value in r.items()
            }
            if isinstance(r, dict)
            else str_if_bytes(r),
            "XINFO CONSUMERS": lambda r: [
                {str_if_bytes(key): value for key, value in x.items()} for x in r
            ],
            "XINFO GROUPS": lambda r: [
                {str_if_bytes(key): value for key, value in d.items()} for d in r
            ],
        }
    )

    try:
        return connection
    finally:
        await connection.aclose()


def set_fake_kv_store_and_js(port: Union[ConsumerPort, EventsPort]):
    port.nats_adapter.kv_store = FakeKvStore()
    port.nats_adapter.js = FakeJs()


class FakeJs:
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    Msg.ack = AsyncMock()

    async def pull_subscribe(self, subject: str, durable: str, stream: str):
        return self.sub

    @staticmethod
    async def stream_info(name: str):
        pass

    @staticmethod
    async def publish(subject: str, payload: bytes, stream: str):
        pass

    @staticmethod
    async def delete_msg(name: str):
        pass

    @staticmethod
    async def add_consumer(stream: str, config: ConsumerConfig):
        pass

    @staticmethod
    async def delete_stream(name: str):
        pass


class FakeKvStore:
    @classmethod
    async def delete(cls, key: str):
        pass

    @classmethod
    async def get(cls, key: str):
        values = {
            "abc:def": kv_subs,
            "foo:bar": kv_subs,
            f"subscriber:{SUBSCRIBER_NAME}": kv_sub_info,
            "udm:users/user": kv_subs,
        }
        return values[key]

    @classmethod
    async def put(cls, key: str, value: Union[str, dict]):
        pass


async def consumer_port_fake_dependency() -> ConsumerPort:
    port = ConsumerPort()
    set_fake_kv_store_and_js(port)
    return port


async def events_port_fake_dependency() -> EventsPort:
    port = EventsPort()
    set_fake_kv_store_and_js(port)
    return port


async def consumer_port_fake_dependency_without_sub():
    port = await consumer_port_fake_dependency()
    port.nats_adapter.get_subscriber = AsyncMock(return_value=None)
    return port


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
