# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest
from test_helpers.mock_data import FLAT_MESSAGE_ENCODED, MESSAGE, SUBSCRIPTION_NAME

from univention.provisioning.backends.nats_mq import ConsumerQueue, IncomingQueue, PrefillConsumerQueue
from univention.provisioning.models.message import MessageProcessingStatus
from univention.provisioning.models.subscription import FillQueueStatus
from univention.provisioning.rest.message_service import MessageService
from univention.provisioning.rest.mq_adapter_nats import NatsMessageQueue

MESSAGE_PROCESSING_STATUS = MessageProcessingStatus.ok
MESSAGE_PROCESSING_SEQ_ID = 1


@pytest.fixture
def message_service() -> MessageService:
    ms = MessageService(subscriptions_db=AsyncMock(), mq=AsyncMock())
    ms._subscription_prefill_done.clear()
    return ms


@pytest.mark.anyio
class TestMessageService:
    async def test_get_next_message_prefill_running(self, message_service: MessageService):
        message_service.sub_service.get_subscription_queue_status = AsyncMock(return_value=FillQueueStatus.running)

        result = await message_service.get_next_message(SUBSCRIPTION_NAME, timeout=1, pop=True)

        message_service.sub_service.get_subscription_queue_status.assert_has_calls(
            [call(SUBSCRIPTION_NAME), call(SUBSCRIPTION_NAME)]
        )
        message_service.mq.get_message.assert_not_called()
        assert result is None

    async def test_get_next_message_from_prefill_subject(self, message_service: MessageService):
        message_service.sub_service.get_subscription_queue_status = AsyncMock(return_value=FillQueueStatus.done)
        message_service.mq.get_message = AsyncMock(return_value=MESSAGE)

        result = await message_service.get_next_message(SUBSCRIPTION_NAME, timeout=5, pop=True)

        message_service.sub_service.get_subscription_queue_status.assert_called_once_with(SUBSCRIPTION_NAME)
        message_service.mq.get_message.assert_called_once_with(PrefillConsumerQueue(SUBSCRIPTION_NAME), 5, True)
        assert result == MESSAGE

    async def test_get_next_message_from_main_subject(self, message_service: MessageService):
        message_service.sub_service.get_subscription_queue_status = AsyncMock(return_value=FillQueueStatus.done)
        message_service.mq.get_message = AsyncMock(return_value=MESSAGE)
        message_service._subscription_prefill_done[SUBSCRIPTION_NAME] = True

        result = await message_service.get_next_message(SUBSCRIPTION_NAME, timeout=5, pop=True)

        message_service.sub_service.get_subscription_queue_status.assert_not_called()
        message_service.mq.get_message.assert_has_calls([call(ConsumerQueue(SUBSCRIPTION_NAME), 5, True)])
        assert result == MESSAGE

    async def test_post_message_status(self, message_service: MessageService):
        message_service.mq.delete_message = AsyncMock()

        result = await message_service.update_message_status(
            SUBSCRIPTION_NAME, MESSAGE_PROCESSING_SEQ_ID, MESSAGE_PROCESSING_STATUS
        )

        message_service.mq.delete_message.assert_called_once_with(ConsumerQueue(SUBSCRIPTION_NAME), 1)
        assert result is None

    async def test_add_live_message(self):
        mq = NatsMessageQueue()
        mq.mq = AsyncMock()
        message_service = MessageService(subscriptions_db=AsyncMock(), mq=mq)

        await message_service.mq.add_message(IncomingQueue(""), MESSAGE)

        message_service.mq.mq.add_message.assert_called_once_with(IncomingQueue(""), FLAT_MESSAGE_ENCODED)
