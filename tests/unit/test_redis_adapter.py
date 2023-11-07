from unittest.mock import call, patch

from datetime import datetime
from unittest.mock import AsyncMock
import pytest
from fakeredis.aioredis import FakeRedis

from consumer.adapters.redis_adapter import RedisAdapter
from core.models import Message, FillQueueStatus


@pytest.fixture
def redis():
    return FakeRedis()


@pytest.fixture
def redis_adapter(redis: FakeRedis) -> RedisAdapter:
    return RedisAdapter(redis)


@pytest.fixture
def pipeline() -> AsyncMock:
    return patch("src.consumer.adapters.redis_adapter.Redis.pipeline").start()


@pytest.mark.anyio
class TestRedisAdapter:
    subscriber_name = "subscriber_1"
    queue_name = f"queue:{subscriber_name}"
    subscriber_topics = f"subscriber_topics:{subscriber_name}"
    subscriber = f"subscriber:{subscriber_name}"

    message = Message(
        publisher_name="live_message",
        ts=datetime(2023, 11, 3, 12, 34, 56, 789012),
        realm="udm",
        topic="topic_name",
        body={
            "foo": "bar",
            "foo1": "bar1",
        },
    )
    flat_message = {
        "publisher_name": "live_message",
        "ts": "2023-11-03T12:34:56.789012",
        "realm": "udm",
        "topic": "topic_name",
        "body": '{"foo": "bar", "foo1": "bar1"}',
    }

    async def test_add_live_message(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.xadd = AsyncMock()

        result = await redis_adapter.add_live_message(
            self.subscriber_name, self.message
        )
        redis.xadd.assert_called_once_with(self.queue_name, self.flat_message, "*")
        assert result is None

    async def test_add_prefill_message(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.xadd = AsyncMock()

        result = await redis_adapter.add_prefill_message(
            self.subscriber_name, self.message
        )

        redis.xadd.assert_called_once_with(self.queue_name, self.flat_message, "0-*")
        assert result is None

    async def test_delete_prefill_messages(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.xtrim = AsyncMock()

        result = await redis_adapter.delete_prefill_messages(self.subscriber_name)

        redis.xtrim.assert_called_once_with(self.queue_name, minid=1)
        assert result is None

    async def test_get_next_message_empty_stream(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.xread = AsyncMock(return_value={})

        result = await redis_adapter.get_next_message(self.subscriber_name)

        redis.xread.assert_called_once_with(
            {self.queue_name: "0-0"}, count=1, block=None
        )
        assert result == {}

    async def test_get_next_message_return_message(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        expected_result = {self.queue_name: [[("1111", self.flat_message)]]}

        redis.xread = AsyncMock(
            return_value={self.queue_name: [[("1111", self.flat_message)]]}
        )

        result = await redis_adapter.get_next_message(self.subscriber_name)

        redis.xread.assert_called_once_with(
            {self.queue_name: "0-0"}, count=1, block=None
        )
        assert result == expected_result

    async def test_get_messages_empty_stream(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.xrange = AsyncMock(return_value=[])

        result = await redis_adapter.read_stream_by_range(self.subscriber_name)

        redis.xrange.assert_called_once_with(self.queue_name, "-", "+", None)
        assert result == []

    async def test_get_messages_return_messages(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        expected_result = [("0000", self.message), ("1111", self.message)]

        redis.xrange = AsyncMock(
            return_value=[("0000", self.message), ("1111", self.message)]
        )

        result = await redis_adapter.read_stream_by_range(self.subscriber_name)

        redis.xrange.assert_called_once_with(self.queue_name, "-", "+", None)
        assert result == expected_result

    async def test_delete_message(self, redis_adapter: RedisAdapter, redis: FakeRedis):
        redis.xdel = AsyncMock()

        result = await redis_adapter.delete_message(self.subscriber_name, "1111")

        redis.xdel.assert_called_once_with(self.queue_name, "1111")
        assert result is None

    async def test_delete_queue(self, redis_adapter: RedisAdapter, redis: FakeRedis):
        redis.xtrim = AsyncMock()

        result = await redis_adapter.delete_queue(self.subscriber_name)

        redis.xtrim.assert_called_once_with(self.queue_name, maxlen=0)
        assert result is None

    async def test_get_subscriber_names_return_data(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.smembers = AsyncMock(return_value=["subscriber_1", "subscriber_2"])

        result = await redis_adapter.get_subscriber_names()

        redis.smembers.assert_called_once_with("subscribers")
        assert result == ["subscriber_1", "subscriber_2"]

    async def test_get_subscriber_names_empty_result(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.smembers = AsyncMock(return_value=[])

        result = await redis_adapter.get_subscriber_names()

        redis.smembers.assert_called_once_with("subscribers")
        assert result == []

    async def test_get_subscriber_by_name_existing(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.sismember = AsyncMock(return_value=1)

        result = await redis_adapter.get_subscriber_by_name(self.subscriber_name)

        redis.sismember.assert_called_once_with("subscribers", self.subscriber_name)
        assert result == 1

    async def test_get_subscriber_by_name_not_existing(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.sismember = AsyncMock(return_value=0)

        result = await redis_adapter.get_subscriber_by_name(self.subscriber_name)

        redis.sismember.assert_called_once_with("subscribers", self.subscriber_name)
        assert result == 0

    async def test_get_subscriber_info(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.hgetall = AsyncMock(
            return_value={
                "name": self.subscriber_name,
                "fill_queue": True,
                "fill_queue_status": "done",
            }
        )
        result = await redis_adapter.get_subscriber_info(self.subscriber_name)

        redis.hgetall.assert_called_once_with(self.subscriber)
        assert result == {
            "name": self.subscriber_name,
            "fill_queue": True,
            "fill_queue_status": "done",
        }

    async def test_get_subscriber_topics(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.smembers = AsyncMock(return_value=["foo:bar", "abc:def"])

        result = await redis_adapter.get_subscriber_topics(self.subscriber_name)

        redis.smembers.assert_called_once_with(self.subscriber_topics)
        assert result == ["foo:bar", "abc:def"]

    async def test_get_subscriber_topics_without_topics(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.smembers = AsyncMock(return_value=[])

        result = await redis_adapter.get_subscriber_topics(self.subscriber_name)

        redis.smembers.assert_called_once_with(self.subscriber_topics)
        assert result == []

    async def test_add_subscriber(
        self, redis_adapter: RedisAdapter, redis: FakeRedis, pipeline
    ):
        realms_topics = [("foo", "bar"), ("abc", "def")]
        redis.sismember = AsyncMock(return_value=0)
        pipe = pipeline.return_value.__aenter__.return_value

        result = await redis_adapter.add_subscriber(
            self.subscriber_name, realms_topics, True, FillQueueStatus.done
        )

        pipeline.assert_called_once()
        pipe.sadd.assert_has_calls(
            [
                call("subscribers", self.subscriber_name),
                call(self.subscriber_topics, "foo:bar"),
                call(self.subscriber_topics, "abc:def"),
            ]
        )
        pipe.hset.assert_called_once_with(
            self.subscriber,
            mapping={
                "name": self.subscriber_name,
                "fill_queue": 1,
                "fill_queue_status": FillQueueStatus.done,
            },
        )
        pipe.execute.assert_called_once_with()
        assert result is None

    async def test_get_subscriber_queue_status(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.hget = AsyncMock(return_value="value")

        result = await redis_adapter.get_subscriber_queue_status(self.subscriber_name)

        redis.hget.assert_called_once_with(self.subscriber, "fill_queue_status")
        assert result == "value"

    async def test_set_subscriber_queue_status(
        self, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        redis.hset = AsyncMock()

        result = await redis_adapter.set_subscriber_queue_status(
            self.subscriber_name, FillQueueStatus.pending
        )

        redis.hset.assert_called_once_with(
            self.subscriber, "fill_queue_status", FillQueueStatus.pending
        )
        assert result is None

    async def test_delete_subscriber(
        self, pipeline, redis_adapter: RedisAdapter, redis: FakeRedis
    ):
        pipe = pipeline.return_value.__aenter__.return_value

        result = await redis_adapter.delete_subscriber(self.subscriber_name)

        pipe.delete.assert_has_calls(
            [call(self.subscriber_topics), call(self.subscriber)]
        )
        pipe.srem.assert_called_once_with("subscribers", self.subscriber_name)
        pipe.execute.assert_called_once()
        assert result is None
