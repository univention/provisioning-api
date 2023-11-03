from unittest.mock import AsyncMock, call

import pytest
from fakeredis.aioredis import FakeRedis

from consumer.subscriptions.persistence import SubscriptionRepository


@pytest.fixture
def redis():
    return FakeRedis()


@pytest.mark.anyio
class TestSubscriptionRepository:
    async def test_get_subscriber_names_return_data(self, redis: FakeRedis):
        redis.smembers = AsyncMock(return_value=["subscriber_1", "subscriber_2"])
        sub_repo = SubscriptionRepository(redis)

        result = await sub_repo.get_subscriber_names()

        redis.smembers.assert_called_once_with("subscribers")
        assert result == ["subscriber_1", "subscriber_2"]

    async def test_get_subscriber_names_empty_result(self, redis: FakeRedis):
        redis.smembers = AsyncMock(return_value=[])
        sub_repo = SubscriptionRepository(redis)

        result = await sub_repo.get_subscriber_names()

        redis.smembers.assert_called_once_with("subscribers")
        assert result == []

    async def test_get_subscriber_existing(self, redis: FakeRedis):
        name = "subscriber_1"
        redis.sismember = AsyncMock(return_value=1)
        redis.hgetall = AsyncMock(
            return_value={
                "name": name,
                "fill_queue": True,
                "fill_queue_status": "done",
            }
        )
        redis.smembers = AsyncMock(return_value=["foo:bar", "abc:def"])

        sub_repo = SubscriptionRepository(redis)

        result = await sub_repo.get_subscriber(name)

        expected_result = {
            "name": "subscriber_1",
            "realms_topics": [["foo", "bar"], ["abc", "def"]],
            "fill_queue": True,
            "fill_queue_status": "done",
        }
        assert result == expected_result
        redis.sismember.assert_called_once_with("subscribers", "subscriber_1")
        redis.hgetall.assert_called_once_with("subscriber:subscriber_1")
        redis.smembers.assert_called_once_with("subscriber_topics:subscriber_1")

    async def test_get_subscriber_non_existing(self, redis: FakeRedis):
        redis.sismember = AsyncMock(return_value=0)
        redis.hgetall = AsyncMock()
        redis.smembers = AsyncMock()
        sub_repo = SubscriptionRepository(redis)

        with pytest.raises(ValueError) as e:
            await sub_repo.get_subscriber("subscriber")

        assert "Subscriber not found." == str(e.value)
        redis.sismember.assert_called_once_with("subscribers", "subscriber")
        redis.hgetall.assert_not_called()
        redis.smembers.assert_not_called()

    async def test_get_subscribers_by_topics_single_subscriber(self, redis: FakeRedis):
        name = "subscriber_1"
        realms_topics = ["foo:bar", "abc:def"]
        redis.smembers = AsyncMock(side_effect=([name], realms_topics))
        sub_repo = SubscriptionRepository(redis)

        result = await sub_repo.get_subscribers_by_topics()

        assert result == [("foo", "bar", name), ("abc", "def", name)]
        redis.smembers.assert_has_calls(
            [call("subscribers"), call("subscriber_topics:subscriber_1")]
        )

    # async def test_get_subscribers_by_topics_without_realms_topics(self, redis: FakeRedis):
    #     name = "subscriber_1"
    #     realms_topics = []
    #     redis.smembers = AsyncMock(side_effect=([name], realms_topics))
    #     sub_repo = SubscriptionRepository(redis)
    #
    #     result = await sub_repo.get_subscribers_by_topics()
    #
    #     assert result == [("foo", "bar", name), ("abc", "def", name)]
    #     redis.smembers.assert_has_calls(
    #         [
    #             call("subscribers"),
    #             call('subscriber_topics:subscriber_1')
    #         ]
    #     )
