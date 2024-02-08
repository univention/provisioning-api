# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch, call
import pytest

from consumer.messages.service.messages import PrefillKeys
from tests.conftest import MESSAGE, SUBSCRIBER_NAME, REPORT
from consumer.messages.service import MessageService
from shared.models import FillQueueStatus


@pytest.fixture
def sub_service() -> AsyncMock:
    yield patch(
        "consumer.messages.service.messages.SubscriptionService"
    ).start().return_value


@pytest.fixture
def message_service() -> MessageService:
    return MessageService(AsyncMock())


@pytest.mark.anyio
class TestMessageService:
    prefill_queue_name = PrefillKeys.queue_name(SUBSCRIBER_NAME)

    async def test_add_prefill_message(self, message_service: MessageService):
        result = await message_service.add_prefill_message(SUBSCRIBER_NAME, MESSAGE)

        message_service._port.add_message.assert_called_once_with(
            self.prefill_queue_name, MESSAGE
        )
        assert result is None

    async def test_delete_prefill_messages(self, message_service: MessageService):
        result = await message_service.delete_prefill_messages(SUBSCRIBER_NAME)

        message_service._port.delete_prefill_messages.assert_called_once_with(
            SUBSCRIBER_NAME
        )
        assert result is None

    async def test_get_next_message(self, message_service: MessageService, sub_service):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.running
        )
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE])

        result = await message_service.get_next_message(
            SUBSCRIBER_NAME, pop=True, timeout=5, skip_prefill=True
        )

        message_service._port.get_messages.assert_called_once_with(
            SUBSCRIBER_NAME, 5, 1, True
        )
        assert result == MESSAGE

    async def test_get_messages_prefill_running(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.running
        )
        message_service._port.stream_exists = AsyncMock(return_value=True)

        result = await message_service.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=2, pop=True, skip_prefill=False
        )

        sub_service.get_subscriber_queue_status.assert_called_once_with(SUBSCRIBER_NAME)
        message_service._port.stream_exists.assert_called_once_with(
            self.prefill_queue_name
        )
        message_service._port.get_messages.assert_not_called()
        message_service._port.delete_stream.assert_not_called()
        assert result == []

    async def test_get_messages_skip_prefill(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.running
        )
        message_service._port.stream_exists = AsyncMock(return_value=True)
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE, MESSAGE])

        result = await message_service.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=2, pop=True, skip_prefill=True
        )

        sub_service.get_subscriber_queue_status.assert_called_once_with(SUBSCRIBER_NAME)
        message_service._port.stream_exists.assert_called_once_with(
            self.prefill_queue_name
        )
        message_service._port.get_messages.assert_called_once_with(
            SUBSCRIBER_NAME, 5, 2, True
        )
        message_service._port.delete_stream.assert_not_called()
        assert result == [MESSAGE, MESSAGE]

    async def test_get_messages_from_prefill_queue(
        self, message_service: MessageService, sub_service
    ):
        message_service._port.stream_exists = AsyncMock(return_value=True)
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE, MESSAGE])

        result = await message_service.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=2, pop=True, skip_prefill=False
        )

        sub_service.get_subscriber_queue_status.assert_called_once_with(SUBSCRIBER_NAME)
        message_service._port.get_messages.assert_called_once_with(
            self.prefill_queue_name, 5, 2, True
        )
        message_service._port.delete_stream.assert_not_called()
        assert result == [MESSAGE, MESSAGE]

    async def test_get_messages_from_prefill_and_main_queues(
        self, message_service: MessageService, sub_service
    ):
        message_service._port.stream_exists = AsyncMock(return_value=True)
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(
            side_effect=[[MESSAGE], [MESSAGE]]
        )

        result = await message_service.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=2, pop=True, skip_prefill=False
        )

        sub_service.get_subscriber_queue_status.assert_called_once_with(SUBSCRIBER_NAME)
        message_service._port.get_messages.assert_has_calls(
            [
                call(self.prefill_queue_name, 5, 2, True),
                call(SUBSCRIBER_NAME, 5, 1, True),
            ]
        )

        message_service._port.delete_stream.assert_called_once_with(
            self.prefill_queue_name
        )
        assert result == [MESSAGE, MESSAGE]

    async def test_get_messages_from_main_queue(
        self, message_service: MessageService, sub_service
    ):
        message_service._port.stream_exists = AsyncMock(return_value=False)
        sub_service.get_subscriber_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE, MESSAGE])

        result = await message_service.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=2, pop=True, skip_prefill=False
        )

        sub_service.get_subscriber_queue_status.assert_called_once_with(SUBSCRIBER_NAME)
        message_service._port.get_messages.assert_called_once_with(
            SUBSCRIBER_NAME, 5, 2, True
        )

        message_service._port.delete_stream.assert_not_called()
        assert result == [MESSAGE, MESSAGE]

    async def test_remove_message(self, message_service: MessageService):
        message_service._port.delete_message = AsyncMock()

        result = await message_service.delete_messages(SUBSCRIBER_NAME, REPORT)

        message_service._port.delete_message.assert_called_once_with(SUBSCRIBER_NAME, 1)
        assert result is None

    async def test_create_prefill_stream(self, message_service: MessageService):
        result = await message_service.create_prefill_stream(SUBSCRIBER_NAME)

        message_service._port.create_stream.assert_called_once_with(
            PrefillKeys.queue_name(SUBSCRIBER_NAME)
        )
        assert result is None
