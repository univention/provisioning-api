# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call, patch

import pytest

from univention.provisioning.models.constants import (
    DISPATCHER_QUEUE_NAME,
    DISPATCHER_SUBJECT_TEMPLATE,
    PREFILL_SUBJECT_TEMPLATE,
)
from univention.provisioning.models.subscription import FillQueueStatus
from univention.provisioning.rest.message_service import MessageProcessingStatus, MessageService
from univention.provisioning.testing.mock_data import MESSAGE, SUBSCRIPTION_NAME

MESSAGE_PROCESSING_STATUS = MessageProcessingStatus.ok
MESSAGE_PROCESSING_SEQ_ID = 1


@pytest.fixture
def sub_service() -> AsyncMock:
    yield patch("server.services.messages.SubscriptionService").start().return_value


@pytest.fixture
def message_service() -> MessageService:
    ms = MessageService(AsyncMock())
    ms._subscription_prefill_done.clear()
    return ms


@pytest.mark.anyio
class TestMessageService:
    prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subscription=SUBSCRIPTION_NAME)
    main_subject = DISPATCHER_SUBJECT_TEMPLATE.format(subscription=SUBSCRIPTION_NAME)

    async def test_get_next_message_prefill_running(self, message_service: MessageService, sub_service):
        sub_service.get_subscription_queue_status = AsyncMock(return_value=FillQueueStatus.running)

        result = await message_service.get_next_message(SUBSCRIPTION_NAME, timeout=1, pop=True)

        sub_service.get_subscription_queue_status.assert_has_calls([call(SUBSCRIPTION_NAME), call(SUBSCRIPTION_NAME)])
        message_service._port.get_message.assert_not_called()
        assert result is None

    async def test_get_next_message_from_prefill_subject(self, message_service: MessageService, sub_service):
        sub_service.get_subscription_queue_status = AsyncMock(return_value=FillQueueStatus.done)
        message_service._port.get_message = AsyncMock(return_value=MESSAGE)

        result = await message_service.get_next_message(SUBSCRIPTION_NAME, timeout=5, pop=True)

        sub_service.get_subscription_queue_status.assert_called_once_with(SUBSCRIPTION_NAME)
        message_service._port.get_message.assert_called_once_with(SUBSCRIPTION_NAME, self.prefill_subject, 5, True)
        assert result == MESSAGE

    async def test_get_next_message_from_main_subject(self, message_service: MessageService, sub_service):
        sub_service.get_subscription_queue_status = AsyncMock(return_value=FillQueueStatus.done)
        message_service._port.get_message = AsyncMock(return_value=MESSAGE)
        message_service._subscription_prefill_done[SUBSCRIPTION_NAME] = True

        result = await message_service.get_next_message(SUBSCRIPTION_NAME, timeout=5, pop=True)

        sub_service.get_subscription_queue_status.assert_not_called()
        message_service._port.get_message.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, self.main_subject, 5, True),
            ]
        )
        assert result == MESSAGE

    async def test_post_message_status(self, message_service: MessageService):
        message_service._port.delete_message = AsyncMock()

        result = await message_service.post_message_status(
            SUBSCRIPTION_NAME, MESSAGE_PROCESSING_SEQ_ID, MESSAGE_PROCESSING_STATUS
        )

        message_service._port.delete_message.assert_called_once_with(SUBSCRIPTION_NAME, 1)
        assert result is None

    async def test_add_live_message(self, message_service: MessageService):
        await message_service.add_live_event(MESSAGE)

        message_service._port.add_message.assert_called_once_with(DISPATCHER_QUEUE_NAME, DISPATCHER_QUEUE_NAME, MESSAGE)
