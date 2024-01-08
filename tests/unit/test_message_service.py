from unittest.mock import AsyncMock, patch
import pytest

from tests.conftest import FLAT_MESSAGE, MESSAGE, SUBSCRIBER_NAME
from consumer.messages.service import MessageService
from shared.models import FillQueueStatus
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
    async def test_add_prefill_message(self, message_service: MessageService):
        message_service._port.add_prefill_message = AsyncMock()

        result = await message_service.add_prefill_message(SUBSCRIBER_NAME, MESSAGE)

        message_service._port.add_prefill_message.assert_called_once_with(
            SUBSCRIBER_NAME, MESSAGE
        )
        assert result is None

    async def test_delete_prefill_messages(self, message_service: MessageService):
        message_service._port.delete_prefill_messages = AsyncMock()

        result = await message_service.delete_prefill_messages(SUBSCRIBER_NAME)

        message_service._port.delete_prefill_messages.assert_called_once_with(
            SUBSCRIBER_NAME
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
            SUBSCRIBER_NAME, pop=False, timeout=5, force=False
        )

        message_service._port.get_next_message.assert_called_once_with(
            SUBSCRIBER_NAME, 5, False
        )
        assert result is None

    async def test_get_next_message_return_message(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_next_message = AsyncMock(return_value=[MESSAGE])
        expected_result = MESSAGE

        result = await message_service.get_next_message(
            SUBSCRIBER_NAME, pop=False, timeout=5
        )

        message_service._port.get_next_message.assert_called_once_with(
            SUBSCRIBER_NAME, 5, False
        )
        assert result == expected_result

    async def test_get_messages_empty_stream(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(return_value=[])

        result = await message_service.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=2, pop=False, force=False
        )

        message_service._port.get_messages.assert_called_once_with(
            SUBSCRIBER_NAME, 5, 2, False
        )
        assert result == []

    async def test_get_messages_return_messages(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE, MESSAGE])
        expected_result = [MESSAGE, MESSAGE]

        result = await message_service.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=2, pop=False, force=False
        )

        message_service._port.get_messages.assert_called_once_with(
            SUBSCRIBER_NAME, 5, 2, False
        )
        assert result == expected_result

    async def test_remove_message(self, message_service: MessageService):
        message_service._port.remove_message = AsyncMock()
        msg = NatsMessage(data=FLAT_MESSAGE)

        result = await message_service.remove_message(msg)

        message_service._port.remove_message.assert_called_once_with(msg)
        assert result is None

    async def test_delete_queue(self, message_service: MessageService):
        message_service._port.delete_queue = AsyncMock()

        result = await message_service.delete_queue(SUBSCRIBER_NAME)

        message_service._port.delete_queue.assert_called_once_with(SUBSCRIBER_NAME)
        assert result is None
