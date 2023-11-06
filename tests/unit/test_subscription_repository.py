from unittest.mock import AsyncMock, call, patch
import pytest
from fakeredis.aioredis import FakeRedis

from consumer.subscriptions.persistence import SubscriptionRepository
from core.models import FillQueueStatus


@pytest.fixture
def redis():
    return FakeRedis()


@pytest.fixture
def pipeline() -> AsyncMock:
    return patch(
        "src.consumer.subscriptions.persistence.subscriptions.redis.Redis.pipeline"
    ).start()


NAME = "subscriber_1"
SUBSCRIBER_TOPICS = f"subscriber_topics:{NAME}"
SUBSCRIBER = f"subscriber:{NAME}"


@pytest.mark.anyio
class TestSubscriptionRepository:
    async def test_get_subscriber_names_return_data(self, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        redis.smembers = AsyncMock(return_value=["subscriber_1", "subscriber_2"])

        result = await sub_repo.get_subscriber_names()

        redis.smembers.assert_called_once_with("subscribers")
        assert result == ["subscriber_1", "subscriber_2"]

    async def test_get_subscriber_names_empty_result(self, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        redis.smembers = AsyncMock(return_value=[])

        result = await sub_repo.get_subscriber_names()

        redis.smembers.assert_called_once_with("subscribers")
        assert result == []

    async def test_get_subscriber_existing(self, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=1)
        redis.hgetall = AsyncMock(
            return_value={
                "name": NAME,
                "fill_queue": True,
                "fill_queue_status": "done",
            }
        )
        redis.smembers = AsyncMock(return_value=["foo:bar", "abc:def"])
        expected_result = {
            "name": NAME,
            "realms_topics": [["foo", "bar"], ["abc", "def"]],
            "fill_queue": True,
            "fill_queue_status": "done",
        }

        result = await sub_repo.get_subscriber(NAME)

        redis.sismember.assert_called_once_with("subscribers", NAME)
        redis.hgetall.assert_called_once_with(SUBSCRIBER)
        redis.smembers.assert_called_once_with(SUBSCRIBER_TOPICS)
        assert result == expected_result

    async def test_get_subscriber_non_existing(self, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=0)
        redis.hgetall = AsyncMock()
        redis.smembers = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_repo.get_subscriber(NAME)

        redis.sismember.assert_called_once_with("subscribers", NAME)
        redis.hgetall.assert_not_called()
        redis.smembers.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscribers_by_topics_single_subscriber(self, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        realms_topics = ["foo:bar", "abc:def"]
        redis.smembers = AsyncMock(side_effect=([NAME], realms_topics))

        result = await sub_repo.get_subscribers_by_topics()

        redis.smembers.assert_has_calls([call("subscribers"), call(SUBSCRIBER_TOPICS)])
        assert result == [("foo", "bar", NAME), ("abc", "def", NAME)]

    async def test_get_subscribers_by_topics_without_realms_topics(
        self, redis: FakeRedis
    ):
        sub_repo = SubscriptionRepository(redis)

        realms_topics = []
        redis.smembers = AsyncMock(side_effect=([NAME], realms_topics))

        result = await sub_repo.get_subscribers_by_topics()

        redis.smembers.assert_has_calls([call("subscribers"), call(SUBSCRIBER_TOPICS)])
        assert result == []

    async def test_add_subscriber_already_exists(self, redis: FakeRedis, pipeline):
        sub_repo = SubscriptionRepository(redis)

        realms_topics = [("foo", "bar"), ("abc", "def")]
        redis.sismember = AsyncMock(return_value=1)

        with pytest.raises(ValueError) as e:
            await sub_repo.add_subscriber(
                NAME, realms_topics, True, FillQueueStatus.done
            )

        redis.sismember.assert_called_once_with("subscribers", NAME)
        pipeline.assert_not_called()
        assert "Subscriber already exists." == str(e.value)

    async def test_add_subscriber(self, redis: FakeRedis, pipeline):
        sub_repo = SubscriptionRepository(redis)

        realms_topics = [("foo", "bar"), ("abc", "def")]
        redis.sismember = AsyncMock(return_value=0)
        pipe = pipeline.return_value.__aenter__.return_value

        result = await sub_repo.add_subscriber(
            NAME, realms_topics, True, FillQueueStatus.done
        )

        pipeline.assert_called_once()
        pipe.sadd.assert_has_calls(
            [
                call("subscribers", NAME),
                call(SUBSCRIBER_TOPICS, "foo:bar"),
                call(SUBSCRIBER_TOPICS, "abc:def"),
            ]
        )
        pipe.hset.assert_called_once_with(
            SUBSCRIBER,
            mapping={
                "name": NAME,
                "fill_queue": 1,
                "fill_queue_status": FillQueueStatus.done,
            },
        )
        pipe.execute.assert_called_once_with()
        assert result is None

    async def test_get_subscriber_queue_status_with_no_subscriber(
        self, redis: FakeRedis
    ):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=0)
        redis.hget = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_repo.get_subscriber_queue_status(NAME)

        redis.hget.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(self, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=1)
        redis.hget = AsyncMock(return_value="value")

        result = await sub_repo.get_subscriber_queue_status(NAME)

        redis.hget.assert_called_once_with(SUBSCRIBER, "fill_queue_status")
        assert result == "value"

    async def test_set_subscriber_queue_status_with_no_subscriber(
        self, redis: FakeRedis
    ):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=0)
        redis.hset = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_repo.set_subscriber_queue_status(NAME, FillQueueStatus.done)

        redis.hset.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_set_subscriber_queue_status_with_subscribers(self, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=1)
        redis.hset = AsyncMock()

        result = await sub_repo.set_subscriber_queue_status(
            NAME, FillQueueStatus.pending
        )

        redis.hset.assert_called_once_with(
            SUBSCRIBER, "fill_queue_status", FillQueueStatus.pending
        )
        assert result is None

    async def test_delete_subscriber_with_no_subscribers(
        self, redis: FakeRedis, pipeline
    ):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=0)

        with pytest.raises(ValueError) as e:
            await sub_repo.delete_subscriber(NAME)

        pipeline.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_delete_subscriber_with_subscribers(self, pipeline, redis: FakeRedis):
        sub_repo = SubscriptionRepository(redis)

        redis.sismember = AsyncMock(return_value=1)
        pipe = pipeline.return_value.__aenter__.return_value

        result = await sub_repo.delete_subscriber(NAME)

        pipe.delete.assert_has_calls([call(SUBSCRIBER_TOPICS), call(SUBSCRIBER)])
        pipe.srem.assert_called_once_with("subscribers", NAME)
        pipe.execute.assert_called_once()
        assert result is None
