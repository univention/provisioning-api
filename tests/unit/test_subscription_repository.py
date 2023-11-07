from unittest.mock import AsyncMock, patch
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


@pytest.fixture
def port() -> AsyncMock:
    return (
        patch("src.consumer.subscriptions.persistence.subscriptions.Port")
        .start()
        .return_value
    )


@pytest.mark.anyio
class TestSubscriptionRepository:
    subscriber_name = "subscriber_1"

    async def test_get_subscriber_names_return_data(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_names = AsyncMock(
            return_value=["subscriber_1", "subscriber_2"]
        )

        result = await sub_repo.get_subscriber_names()

        port.get_subscriber_names.assert_called_once()
        assert result == ["subscriber_1", "subscriber_2"]

    async def test_get_subscriber_names_empty_result(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_names = AsyncMock(return_value=[])

        result = await sub_repo.get_subscriber_names()

        port.get_subscriber_names.assert_called_once_with()
        assert result == []

    async def test_get_subscriber_existing(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=1)
        port.get_subscriber_info = AsyncMock(
            return_value={
                "name": self.subscriber_name,
                "fill_queue": True,
                "fill_queue_status": "done",
            }
        )
        port.get_subscriber_topics = AsyncMock(return_value=["foo:bar", "abc:def"])
        expected_result = {
            "name": self.subscriber_name,
            "realms_topics": [["foo", "bar"], ["abc", "def"]],
            "fill_queue": True,
            "fill_queue_status": "done",
        }

        result = await sub_repo.get_subscriber(self.subscriber_name)

        port.get_subscriber_by_name(self.subscriber_name)
        port.get_subscriber_info(self.subscriber_name)
        port.get_subscriber_topics(self.subscriber_name)
        assert result == expected_result

    async def test_get_subscriber_non_existing(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=0)
        port.get_subscriber_info = AsyncMock()
        port.get_subscriber_topics = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_repo.get_subscriber(self.subscriber_name)

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.get_subscriber_info.assert_not_called()
        port.get_subscriber_topics.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscribers_by_topics_single_subscriber(
        self, redis: FakeRedis, port
    ):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        realms_topics = ["foo:bar", "abc:def"]
        port.get_subscriber_names = AsyncMock(return_value=[self.subscriber_name])
        port.get_subscriber_topics = AsyncMock(return_value=realms_topics)

        result = await sub_repo.get_subscribers_by_topics()

        port.get_subscriber_names.assert_called_once_with()
        port.get_subscriber_topics.assert_called_once_with(self.subscriber_name)
        assert result == [
            ("foo", "bar", self.subscriber_name),
            ("abc", "def", self.subscriber_name),
        ]

    async def test_get_subscribers_by_topics_without_realms_topics(
        self, redis: FakeRedis, port
    ):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        realms_topics = []
        port.get_subscriber_names = AsyncMock(return_value=[self.subscriber_name])
        port.get_subscriber_topics = AsyncMock(return_value=realms_topics)

        result = await sub_repo.get_subscribers_by_topics()

        port.get_subscriber_names.assert_called_once_with()
        port.get_subscriber_topics.assert_called_once_with(self.subscriber_name)
        assert result == []

    async def test_add_subscriber_already_exists(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        realms_topics = [("foo", "bar"), ("abc", "def")]
        port.get_subscriber_by_name = AsyncMock(return_value=1)

        with pytest.raises(ValueError) as e:
            await sub_repo.add_subscriber(
                self.subscriber_name, realms_topics, True, FillQueueStatus.done
            )

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.add_subscriber.assert_not_called()
        assert "Subscriber already exists." == str(e.value)

    async def test_add_subscriber(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        realms_topics = [("foo", "bar"), ("abc", "def")]
        port.get_subscriber_by_name = AsyncMock(return_value=0)
        port.add_subscriber = AsyncMock()

        result = await sub_repo.add_subscriber(
            self.subscriber_name, realms_topics, True, FillQueueStatus.done
        )

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.add_subscriber.assert_called_once_with(
            self.subscriber_name, realms_topics, True, FillQueueStatus.done
        )
        assert result is None

    async def test_get_subscriber_queue_status_with_no_subscriber(
        self, redis: FakeRedis, port
    ):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=0)
        port.get_subscriber_queue_status = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_repo.get_subscriber_queue_status(self.subscriber_name)

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.get_subscriber_queue_status.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(
        self, redis: FakeRedis, port
    ):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=1)
        port.get_subscriber_queue_status = AsyncMock(return_value="value")

        result = await sub_repo.get_subscriber_queue_status(self.subscriber_name)

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.get_subscriber_queue_status(self.subscriber_name, "fill_queue_status")
        assert result == "value"

    async def test_set_subscriber_queue_status_with_no_subscriber(
        self, redis: FakeRedis, port
    ):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=0)
        port.set_subscriber_queue_status = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_repo.get_subscriber_queue_status(self.subscriber_name)

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.set_subscriber_queue_status.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_set_subscriber_queue_status_with_subscribers(
        self, redis: FakeRedis, port
    ):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=1)
        port.set_subscriber_queue_status = AsyncMock()

        result = await sub_repo.set_subscriber_queue_status(
            self.subscriber_name, FillQueueStatus.pending
        )

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.set_subscriber_queue_status.assert_called_once_with(
            self.subscriber_name, FillQueueStatus.pending
        )
        assert result is None

    async def test_delete_subscriber_with_no_subscribers(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=0)
        port.delete_subscriber = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_repo.delete_subscriber(self.subscriber_name)

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.delete_subscriber.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_delete_subscriber_with_subscribers(self, redis: FakeRedis, port):
        sub_repo = SubscriptionRepository(redis)
        sub_repo.port = port

        port.get_subscriber_by_name = AsyncMock(return_value=1)
        port.delete_subscriber = AsyncMock()

        result = await sub_repo.delete_subscriber(self.subscriber_name)

        port.get_subscriber_by_name.assert_called_once_with(self.subscriber_name)
        port.delete_subscriber.assert_called_once_with(self.subscriber_name)
        assert result is None
