# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import call, patch

from unittest.mock import AsyncMock
import pytest
from fakeredis.aioredis import FakeRedis

from tests.conftest import FLAT_MESSAGE, MESSAGE, SUBSCRIBER_NAME
from shared.adapters.redis_adapter import RedisAdapter
from shared.models import FillQueueStatus


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def redis_adapter(fake_redis) -> RedisAdapter:
    redis_adapter = RedisAdapter()
    redis_adapter.redis = fake_redis
    return redis_adapter


@pytest.fixture
def pipeline() -> AsyncMock:
    return patch("src.shared.adapters.redis_adapter.Redis.pipeline").start()


@pytest.mark.anyio
class TestRedisAdapter:
    queue_name = f"queue:{SUBSCRIBER_NAME}"
    subscriber_topics = f"subscriber_topics:{SUBSCRIBER_NAME}"
    subscriber = f"subscriber:{SUBSCRIBER_NAME}"

    async def test_add_live_message(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.xadd = AsyncMock()

        result = await redis_adapter.add_live_message(SUBSCRIBER_NAME, MESSAGE)
        fake_redis.xadd.assert_called_once()
        fake_redis.xadd.assert_called_once_with(self.queue_name, FLAT_MESSAGE, "*")
        assert result is None

    async def test_add_prefill_message(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.xadd = AsyncMock()

        result = await redis_adapter.add_prefill_message(SUBSCRIBER_NAME, MESSAGE)

        fake_redis.xadd.assert_called_once_with(self.queue_name, FLAT_MESSAGE, "0-*")
        assert result is None

    async def test_delete_prefill_messages(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.xtrim = AsyncMock()

        result = await redis_adapter.delete_prefill_messages(SUBSCRIBER_NAME)

        fake_redis.xtrim.assert_called_once_with(self.queue_name, minid=1)
        assert result is None

    async def test_get_next_message_empty_stream(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.xread = AsyncMock(return_value={})

        result = await redis_adapter.get_next_message(SUBSCRIBER_NAME)

        fake_redis.xread.assert_called_once_with(
            {self.queue_name: "0-0"}, count=1, block=None
        )
        assert result == {}

    async def test_get_next_message_return_message(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        expected_result = {self.queue_name: [[("1111", FLAT_MESSAGE)]]}

        fake_redis.xread = AsyncMock(
            return_value={self.queue_name: [[("1111", FLAT_MESSAGE)]]}
        )

        result = await redis_adapter.get_next_message(SUBSCRIBER_NAME)

        fake_redis.xread.assert_called_once_with(
            {self.queue_name: "0-0"}, count=1, block=None
        )
        assert result == expected_result

    async def test_get_messages_empty_stream(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.xrange = AsyncMock(return_value=[])

        result = await redis_adapter.get_messages(SUBSCRIBER_NAME)

        fake_redis.xrange.assert_called_once_with(self.queue_name, "-", "+", None)
        assert result == []

    async def test_get_messages_return_messages(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        expected_result = [("0000", MESSAGE), ("1111", MESSAGE)]

        fake_redis.xrange = AsyncMock(
            return_value=[("0000", FLAT_MESSAGE), ("1111", FLAT_MESSAGE)]
        )

        result = await redis_adapter.get_messages(SUBSCRIBER_NAME)

        fake_redis.xrange.assert_called_once_with(self.queue_name, "-", "+", None)
        assert result == expected_result

    async def test_delete_message(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.xdel = AsyncMock()

        result = await redis_adapter.delete_message(SUBSCRIBER_NAME, "1111")

        fake_redis.xdel.assert_called_once_with(self.queue_name, "1111")
        assert result is None

    async def test_delete_queue(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.xtrim = AsyncMock()

        result = await redis_adapter.delete_queue(SUBSCRIBER_NAME)

        fake_redis.xtrim.assert_called_once_with(self.queue_name, maxlen=0)
        assert result is None

    async def test_get_subscriber_names_return_data(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.smembers = AsyncMock(return_value=["subscriber_1", "subscriber_2"])

        result = await redis_adapter.get_subscriber_names()

        fake_redis.smembers.assert_called_once_with("subscribers")
        assert result == ["subscriber_1", "subscriber_2"]

    async def test_get_subscriber_names_empty_result(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.smembers = AsyncMock(return_value=[])

        result = await redis_adapter.get_subscriber_names()

        fake_redis.smembers.assert_called_once_with("subscribers")
        assert result == []

    async def test_get_subscriber_by_name_existing(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.sismember = AsyncMock(return_value=1)

        result = await redis_adapter.get_subscriber_by_name(SUBSCRIBER_NAME)

        fake_redis.sismember.assert_called_once_with("subscribers", SUBSCRIBER_NAME)
        assert result == 1

    async def test_get_subscriber_by_name_not_existing(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.sismember = AsyncMock(return_value=0)

        result = await redis_adapter.get_subscriber_by_name(SUBSCRIBER_NAME)

        fake_redis.sismember.assert_called_once_with("subscribers", SUBSCRIBER_NAME)
        assert result == 0

    async def test_get_subscriber_info(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.hgetall = AsyncMock(
            return_value={
                "name": SUBSCRIBER_NAME,
                "request_prefill": True,
                "prefill_queue_status": "done",
            }
        )
        result = await redis_adapter.get_subscriber_info(SUBSCRIBER_NAME)

        fake_redis.hgetall.assert_called_once_with(self.subscriber)
        assert result == {
            "name": SUBSCRIBER_NAME,
            "request_prefill": True,
            "prefill_queue_status": "done",
        }

    async def test_get_subscriber_topics(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.smembers = AsyncMock(return_value=["foo:bar", "abc:def"])

        result = await redis_adapter.get_subscriber_topics(SUBSCRIBER_NAME)

        fake_redis.smembers.assert_called_once_with(self.subscriber_topics)
        assert result == ["foo:bar", "abc:def"]

    async def test_get_subscriber_topics_without_topics(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.smembers = AsyncMock(return_value=[])

        result = await redis_adapter.get_subscriber_topics(SUBSCRIBER_NAME)

        fake_redis.smembers.assert_called_once_with(self.subscriber_topics)
        assert result == []

    async def test_add_subscriber(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis, pipeline
    ):
        realms_topics = [("foo", "bar"), ("abc", "def")]
        fake_redis.sismember = AsyncMock(return_value=0)
        pipe = pipeline.return_value.__aenter__.return_value

        result = await redis_adapter.add_subscriber(
            SUBSCRIBER_NAME, realms_topics, True, FillQueueStatus.done
        )

        pipeline.assert_called_once()
        pipe.sadd.assert_has_calls(
            [
                call("subscribers", SUBSCRIBER_NAME),
                call(self.subscriber_topics, "foo:bar"),
                call(self.subscriber_topics, "abc:def"),
            ]
        )
        pipe.hset.assert_called_once_with(
            self.subscriber,
            mapping={
                "name": SUBSCRIBER_NAME,
                "request_prefill": 1,
                "prefill_queue_status": FillQueueStatus.done,
            },
        )
        pipe.execute.assert_called_once_with()
        assert result is None

    async def test_get_subscriber_queue_status(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.hget = AsyncMock(return_value="value")

        result = await redis_adapter.get_subscriber_queue_status(SUBSCRIBER_NAME)

        fake_redis.hget.assert_called_once_with(self.subscriber, "prefill_queue_status")
        assert result == "value"

    async def test_set_subscriber_queue_status(
        self, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        fake_redis.hset = AsyncMock()

        result = await redis_adapter.set_subscriber_queue_status(
            SUBSCRIBER_NAME, FillQueueStatus.pending
        )

        fake_redis.hset.assert_called_once_with(
            self.subscriber, "prefill_queue_status", FillQueueStatus.pending
        )
        assert result is None

    async def test_delete_subscriber(
        self, pipeline, redis_adapter: RedisAdapter, fake_redis: FakeRedis
    ):
        pipe = pipeline.return_value.__aenter__.return_value

        result = await redis_adapter.delete_subscriber(SUBSCRIBER_NAME)

        pipe.delete.assert_has_calls(
            [call(self.subscriber_topics), call(self.subscriber)]
        )
        pipe.srem.assert_called_once_with("subscribers", SUBSCRIBER_NAME)
        pipe.execute.assert_called_once()
        assert result is None
