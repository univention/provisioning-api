from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest

from consumer.messages.service import MessageService
from shared.models import Message, NewMessage, FillQueueStatus
from shared.models.queue import NatsMessage


@pytest.fixture
def port() -> AsyncMock:
    return patch("consumer.messages.service.messages.ConsumerPort").start().return_value


@pytest.fixture
def sub_service() -> AsyncMock:
    yield patch(
        "consumer.messages.service.messages.SubscriptionService"
    ).start().return_value


@pytest.fixture
def message_service(port, sub_service) -> MessageService:
    message_repo = MessageService(port)
    return message_repo


@pytest.mark.anyio
class TestMessageService:
    subscriber_name = "subscriber_1"
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

    async def test_add_live_message(self, message_service: MessageService, sub_service):
        data = NewMessage(
            realm="udm", topic="topic_name", body={"foo": "bar", "foo1": "bar1"}
        )
        message_service._port.get_subscribers_for_topic = AsyncMock(
            return_value=[self.subscriber_name]
        )
        message_service._port.add_live_message = AsyncMock()

        await message_service.publish_message(data, "live_message", self.message.ts)

        message_service._port.add_live_message.assert_called_once_with(
            self.subscriber_name, self.message
        )
        message_service._port.get_subscribers_for_topic.assert_called_once_with(
            "udm:topic_name"
        )

    async def test_add_prefill_message(self, message_service: MessageService):
        message_service._port.add_prefill_message = AsyncMock()

        result = await message_service.add_prefill_message(
            self.subscriber_name, self.message
        )

        message_service._port.add_prefill_message.assert_called_once_with(
            self.subscriber_name, self.message
        )
        assert result is None

    async def test_delete_prefill_messages(self, message_service: MessageService):
        message_service._port.delete_prefill_messages = AsyncMock()

        result = await message_service.delete_prefill_messages(self.subscriber_name)

        message_service._port.delete_prefill_messages.assert_called_once_with(
            self.subscriber_name
        )
        assert result is None

    async def test_get_next_message_empty_stream(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_next_message = AsyncMock(return_value=[])

        result = await message_service.get_next_message(
            self.subscriber_name, False, 5, False
        )

        message_service._port.get_next_message.assert_called_once_with(
            self.subscriber_name, 5, False
        )
        assert result is None

    async def test_get_next_message_return_message(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_next_message = AsyncMock(return_value=[self.message])
        expected_result = self.message

        result = await message_service.get_next_message(self.subscriber_name, False, 5)

        message_service._port.get_next_message.assert_called_once_with(
            self.subscriber_name, 5, False
        )
        assert result == expected_result

    async def test_get_messages_empty_stream(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(return_value=[])

        result = await message_service.get_messages(self.subscriber_name, 5, 2, False)

        message_service._port.get_messages.assert_called_once_with(
            self.subscriber_name, 5, 2, False
        )
        assert result == []

    async def test_get_messages_return_messages(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(
            return_value=[self.message, self.message]
        )
        expected_result = [self.message, self.message]

        result = await message_service.get_messages(self.subscriber_name, 5, 2, False)

        message_service._port.get_messages.assert_called_once_with(
            self.subscriber_name, 5, 2, False
        )
        assert result == expected_result

    async def test_remove_message(self, message_service: MessageService):
        message_service._port.remove_message = AsyncMock()
        msg = NatsMessage(data=self.flat_message)

        result = await message_service.remove_message(msg)

        message_service._port.remove_message.assert_called_once_with(msg)
        assert result is None

    async def test_delete_queue(self, message_service: MessageService):
        message_service._port.delete_queue = AsyncMock()

        result = await message_service.delete_queue(self.subscriber_name)

        message_service._port.delete_queue.assert_called_once_with(self.subscriber_name)
        assert result is None
