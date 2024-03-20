# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch, call
import pytest
from shared.services.messages import MessageService, PREFILL_SUBJECT_TEMPLATE
from tests.conftest import MESSAGE, REPORT, SUBSCRIPTION_NAME
from shared.models import FillQueueStatus


@pytest.fixture
def sub_service() -> AsyncMock:
    yield patch("shared.services.messages.SubscriptionService").start().return_value


@pytest.fixture
def message_service() -> MessageService:
    return MessageService(AsyncMock())


@pytest.mark.anyio
class TestMessageService:
    prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subject=SUBSCRIPTION_NAME)

    async def test_get_next_message(self, message_service: MessageService, sub_service):
        sub_service.get_subscription_queue_status = AsyncMock(
            return_value=FillQueueStatus.running
        )
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE])
        message_service._port.stream_exists = AsyncMock(return_value=False)

        result = await message_service.get_next_message(
            SUBSCRIPTION_NAME, pop=True, timeout=5
        )

        message_service._port.get_messages.assert_called_once_with(
            SUBSCRIPTION_NAME, 5, 1, True
        )
        assert result == MESSAGE

    async def test_get_messages_prefill_running(
        self, message_service: MessageService, sub_service
    ):
        sub_service.get_subscription_queue_status = AsyncMock(
            return_value=FillQueueStatus.running
        )
        message_service._port.stream_exists = AsyncMock(return_value=True)

        result = await message_service.get_messages(
            SUBSCRIPTION_NAME, timeout=5, count=2, pop=True
        )

        sub_service.get_subscription_queue_status.assert_called_once_with(
            SUBSCRIPTION_NAME
        )
        message_service._port.stream_exists.assert_called_once_with(
            self.prefill_subject
        )
        message_service._port.get_messages.assert_not_called()
        message_service._port.delete_stream.assert_not_called()
        assert result == []

    async def test_get_messages_from_prefill_queue(
        self, message_service: MessageService, sub_service
    ):
        message_service._port.stream_exists = AsyncMock(return_value=True)
        sub_service.get_subscription_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE, MESSAGE])

        result = await message_service.get_messages(
            SUBSCRIPTION_NAME, timeout=5, count=2, pop=True
        )

        sub_service.get_subscription_queue_status.assert_called_once_with(
            SUBSCRIPTION_NAME
        )
        message_service._port.get_messages.assert_called_once_with(
            self.prefill_subject, 5, 2, True
        )
        message_service._port.delete_stream.assert_not_called()
        assert result == [MESSAGE, MESSAGE]

    async def test_get_messages_from_prefill_and_main_queues(
        self, message_service: MessageService, sub_service
    ):
        message_service._port.stream_exists = AsyncMock(return_value=True)
        sub_service.get_subscription_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(
            side_effect=[[MESSAGE], [MESSAGE]]
        )

        result = await message_service.get_messages(
            SUBSCRIPTION_NAME, timeout=5, count=2, pop=True
        )

        sub_service.get_subscription_queue_status.assert_called_once_with(
            SUBSCRIPTION_NAME
        )
        message_service._port.get_messages.assert_has_calls(
            [
                call(self.prefill_subject, 5, 2, True),
                call(SUBSCRIPTION_NAME, 5, 1, True),
            ]
        )

        message_service._port.delete_stream.assert_called_once_with(
            self.prefill_subject
        )
        assert result == [MESSAGE, MESSAGE]

    async def test_get_messages_from_main_queue(
        self, message_service: MessageService, sub_service
    ):
        message_service._port.stream_exists = AsyncMock(return_value=False)
        sub_service.get_subscription_queue_status = AsyncMock(
            return_value=FillQueueStatus.done
        )
        message_service._port.get_messages = AsyncMock(return_value=[MESSAGE, MESSAGE])

        result = await message_service.get_messages(
            SUBSCRIPTION_NAME, timeout=5, count=2, pop=True
        )

        sub_service.get_subscription_queue_status.assert_called_once_with(
            SUBSCRIPTION_NAME
        )
        message_service._port.get_messages.assert_called_once_with(
            SUBSCRIPTION_NAME, 5, 2, True
        )

        message_service._port.delete_stream.assert_not_called()
        assert result == [MESSAGE, MESSAGE]

    async def test_remove_message(self, message_service: MessageService):
        message_service._port.delete_message = AsyncMock()

        result = await message_service.delete_message(SUBSCRIPTION_NAME, REPORT)

        message_service._port.delete_message.assert_called_once_with(
            SUBSCRIPTION_NAME, 1
        )
        assert result is None

    async def test_add_live_message(self, message_service: MessageService):
        await message_service.add_live_event(MESSAGE)

        message_service._port.add_message.assert_called_once_with("incoming", MESSAGE)
