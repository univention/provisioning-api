import json
from unittest.mock import AsyncMock, Mock

import pytest
from fakeredis import aioredis
from nats.aio.msg import Msg
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

FLAT_MESSAGE = {
    "publisher_name": "127.0.0.1",
    "ts": "2023-11-09T11:15:52.616061",
    "realm": "foo",
    "topic": "bar/baz",
    "body": '{"hello": "world"}',
}


async def redis_fake_dependency():
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
        yield connection
    finally:
        await connection.aclose()


async def nats_fake_dependency():
    server = AsyncMock()
    js = Mock()
    server.jetstream = Mock(return_value=js)
    js.stream_info = AsyncMock()
    js.publish = AsyncMock()
    js.delete_msg = AsyncMock()
    js.add_consumer = AsyncMock()
    js.delete_stream = AsyncMock()

    sub = AsyncMock()
    js.pull_subscribe = AsyncMock(return_value=sub)
    sub.fetch = AsyncMock(
        return_value=[Msg(_client=server, data=json.dumps(FLAT_MESSAGE).encode())]
    )
    return server


async def port_fake_dependency():
    pass


@pytest.fixture(scope="session", autouse=True)
def override_dependencies():
    # Override original port
    app.dependency_overrides[ConsumerPort.port_dependency] = port_fake_dependency
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
