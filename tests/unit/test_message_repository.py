from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest
from fakeredis.aioredis import FakeRedis

from consumer.messages.persistence import MessageRepository
from core.models import Message


@pytest.fixture
def redis():
    return FakeRedis()


@pytest.fixture
def port() -> AsyncMock:
    return patch("src.consumer.messages.persistence.messages.Port").start().return_value


@pytest.fixture
def message_repo(redis, port) -> MessageRepository:
    message_repo = MessageRepository(redis)
    message_repo.port = port
    return message_repo


@pytest.mark.anyio
class TestMessageRepository:
    subscriber_name = "subscriber_1"
    queue_name = f"queue:{subscriber_name}"
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

    async def test_add_live_message(self, message_repo: MessageRepository):
        message_repo.port.add_live_message = AsyncMock()

        await message_repo.add_live_message(self.subscriber_name, self.message)
        message_repo.port.add_live_message.assert_called_once_with(
            self.subscriber_name, self.message
        )

    async def test_add_prefill_message(self, message_repo: MessageRepository):
        message_repo.port.add_prefill_message = AsyncMock()

        result = await message_repo.add_prefill_message(
            self.subscriber_name, self.message
        )

        message_repo.port.add_prefill_message.assert_called_once_with(
            self.subscriber_name, self.message
        )
        assert result is None

    async def test_delete_prefill_messages(self, message_repo: MessageRepository):
        message_repo.port.delete_prefill_messages = AsyncMock()

        result = await message_repo.delete_prefill_messages(self.subscriber_name)

        message_repo.port.delete_prefill_messages.assert_called_once_with(
            self.subscriber_name
        )
        assert result is None

    async def test_get_next_message_empty_stream(self, message_repo: MessageRepository):
        message_repo.port.read_stream = AsyncMock()

        result = await message_repo.get_next_message(self.subscriber_name)

        message_repo.port.read_stream.assert_called_once_with(
            self.subscriber_name, None
        )
        assert result is None

    async def test_get_next_message_return_message(self, message_repo):
        message_repo.port.read_stream = AsyncMock(
            return_value={self.queue_name: [[("1111", self.flat_message)]]}
        )
        expected_result = ("1111", self.message)

        result = await message_repo.get_next_message(self.subscriber_name)

        message_repo.port.read_stream.assert_called_once_with(
            self.subscriber_name, None
        )
        assert result == expected_result

    async def test_get_messages_empty_stream(self, message_repo):
        message_repo.port.read_stream_by_range = AsyncMock(return_value=[])

        result = await message_repo.get_messages(self.subscriber_name)

        message_repo.port.read_stream_by_range.assert_called_once_with(
            self.subscriber_name, None, "-", "+"
        )
        assert result == []

    async def test_get_messages_return_messages(self, message_repo):
        message_repo.port.read_stream_by_range = AsyncMock(
            return_value=[("0000", self.flat_message), ("1111", self.flat_message)]
        )
        expected_result = [("0000", self.message), ("1111", self.message)]

        result = await message_repo.get_messages(self.subscriber_name)

        message_repo.port.read_stream_by_range.assert_called_once_with(
            self.subscriber_name,
            None,
            "-",
            "+",
        )
        assert result == expected_result

    async def test_delete_message(self, message_repo):
        message_repo.port.delete_message = AsyncMock()

        result = await message_repo.delete_message(self.subscriber_name, "1111")

        message_repo.port.delete_message.assert_called_once_with(
            self.subscriber_name, "1111"
        )
        assert result is None

    async def test_delete_queue(self, message_repo):
        message_repo.port.delete_queue = AsyncMock()

        result = await message_repo.delete_queue(self.subscriber_name)

        message_repo.port.delete_queue.assert_called_once_with(self.subscriber_name)
        assert result is None
