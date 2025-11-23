# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
from unittest.mock import Mock

from univention.provisioning.backends.nats_mq import ConsumerQueue, IncomingQueue, PrefillQueue

try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock

import pytest
from nats.js.errors import NotFoundError
from test_helpers.mock_data import (
    FLAT_MESSAGE_ENCODED,
    MSG,
    NATS_SERVER,
    PROVISIONING_MESSAGE,
    SUBSCRIPTION_NAME,
)


@pytest.mark.anyio
class TestNatsMQAdapter:
    subject = "subject"
    consumer_queue = ConsumerQueue(SUBSCRIPTION_NAME)
    incoming_queue = IncomingQueue(SUBSCRIPTION_NAME)
    prefilling_queue = PrefillQueue()

    async def test_connect(self, mock_nats_mq_adapter, nats_credentials):
        result = await mock_nats_mq_adapter.connect()

        mock_nats_mq_adapter._nats.connect.assert_called_once_with(
            servers=NATS_SERVER,
            user=nats_credentials["username"],
            password=nats_credentials["password"],
            error_cb=mock_nats_mq_adapter.error_callback,
            disconnected_cb=mock_nats_mq_adapter.disconnected_callback,
            closed_cb=mock_nats_mq_adapter.closed_callback,
            reconnected_cb=mock_nats_mq_adapter.reconnected_callback,
            max_reconnect_attempts=5,
        )
        assert result is None

    async def test_close(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.close()

        mock_nats_mq_adapter._nats.close.assert_called_once_with()
        assert result is None

    async def test_add_message_new_stream(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.add_message(self.consumer_queue, FLAT_MESSAGE_ENCODED)

        mock_nats_mq_adapter._js.publish.assert_called_once_with(
            subject=self.consumer_queue.message_subject,
            payload=FLAT_MESSAGE_ENCODED,
            stream=self.consumer_queue.queue_name,
        )
        assert result is None

    async def test_get_messages(self, mock_nats_mq_adapter, mock_fetch):
        consumer_mock = Mock()
        mock_nats_mq_adapter.delete_message = AsyncMock()
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(return_value=consumer_mock)

        result = await mock_nats_mq_adapter.get_message(self.incoming_queue, timeout=5, pop=False)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(self.incoming_queue.queue_name)
        mock_nats_mq_adapter._js.consumer_info.assert_called_once_with(
            self.incoming_queue.queue_name, self.incoming_queue.consumer_name
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            self.incoming_queue.name,
            durable=f"durable_name:{SUBSCRIPTION_NAME}",
            stream=self.incoming_queue.queue_name,
            config=consumer_mock,
        )
        mock_fetch.assert_called_once_with(1, 5)
        mock_nats_mq_adapter.delete_message.assert_not_called()
        assert result == PROVISIONING_MESSAGE

    async def test_get_messages_with_removing(self, mock_nats_mq_adapter, mock_fetch):
        consumer_mock = Mock()
        mock_nats_mq_adapter.delete_message = AsyncMock()
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(return_value=consumer_mock)

        result = await mock_nats_mq_adapter.get_message(self.incoming_queue, timeout=5, pop=True)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(self.incoming_queue.queue_name)
        mock_nats_mq_adapter._js.consumer_info.assert_called_once_with(
            self.incoming_queue.queue_name, self.incoming_queue.consumer_name
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            self.incoming_queue.message_subject,
            durable=self.incoming_queue.consumer_name,
            stream=self.incoming_queue.queue_name,
            config=consumer_mock,
        )
        mock_fetch.assert_called_once_with(1, 5)
        MSG.ack.assert_called_with()
        assert result == PROVISIONING_MESSAGE

    async def test_get_messages_without_stream(self, mock_nats_mq_adapter, mock_fetch):
        mock_nats_mq_adapter._js.stream_info = AsyncMock(side_effect=NotFoundError)
        mock_nats_mq_adapter.delete_message = AsyncMock()

        with pytest.raises(NotFoundError):
            await mock_nats_mq_adapter.get_message(self.consumer_queue, timeout=5, pop=False)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(self.consumer_queue.queue_name)
        mock_nats_mq_adapter._js.pull_subscribe.assert_not_called()
        mock_nats_mq_adapter._js.consumer_info.assert_not_called()
        mock_fetch.assert_not_called()
        mock_nats_mq_adapter.delete_message.assert_not_called()

    async def test_get_messages_without_consumer(self, mock_nats_mq_adapter, mock_fetch):
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(side_effect=NotFoundError)
        mock_nats_mq_adapter.delete_message = AsyncMock()

        with pytest.raises(NotFoundError):
            await mock_nats_mq_adapter.get_message(self.incoming_queue, timeout=5, pop=False)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(self.incoming_queue.queue_name)
        mock_nats_mq_adapter._js.pull_subscribe.assert_not_called()
        mock_nats_mq_adapter._js.consumer_info.assert_called_once_with(
            self.incoming_queue.queue_name, self.incoming_queue.consumer_name
        )
        mock_fetch.assert_not_called()
        mock_nats_mq_adapter.delete_message.assert_not_called()

    async def test_get_messages_timeout_error(self, mock_nats_mq_adapter):
        sub = AsyncMock()
        consumer_mock = Mock()
        sub.fetch = AsyncMock(side_effect=asyncio.TimeoutError)
        mock_nats_mq_adapter._js.pull_subscribe = AsyncMock(return_value=sub)
        mock_nats_mq_adapter.delete_message = AsyncMock()
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(return_value=consumer_mock)

        result = await mock_nats_mq_adapter.get_message(self.incoming_queue, timeout=5, pop=False)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(self.incoming_queue.queue_name)
        mock_nats_mq_adapter._js.consumer_info.assert_called_once_with(
            self.incoming_queue.queue_name, self.incoming_queue.consumer_name
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            self.incoming_queue.message_subject,
            durable=self.incoming_queue.consumer_name,
            stream=self.incoming_queue.queue_name,
            config=consumer_mock,
        )
        sub.fetch.assert_called_once_with(1, 5)
        mock_nats_mq_adapter.delete_message.assert_not_called()
        assert result is None

    async def test_delete_message(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.delete_message(self.consumer_queue, 1)

        mock_nats_mq_adapter._js.get_msg.assert_called_once_with(self.consumer_queue.queue_name, 1)
        mock_nats_mq_adapter._js.delete_msg.assert_called_once_with(self.consumer_queue.queue_name, 1)
        assert result is None

    async def test_delete_message_no_message(self, mock_nats_mq_adapter):
        error = NotFoundError()
        error.description = "Message not found"
        mock_nats_mq_adapter._js.get_msg = AsyncMock(side_effect=error)

        with pytest.raises(ValueError, match="Message not found"):
            await mock_nats_mq_adapter.delete_message(self.consumer_queue, 1)

        mock_nats_mq_adapter._js.get_msg.assert_called_once_with(self.consumer_queue.queue_name, 1)
        mock_nats_mq_adapter._js.delete_msg.assert_not_called()

    async def test_delete_stream(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.delete_stream(self.consumer_queue)

        mock_nats_mq_adapter._js.delete_stream.assert_called_once_with(self.consumer_queue.queue_name)
        assert result is None

    async def test_delete_stream_not_found(self, mock_nats_mq_adapter):
        mock_nats_mq_adapter._js.delete_stream = AsyncMock(side_effect=NotFoundError)

        result = await mock_nats_mq_adapter.delete_stream(self.consumer_queue)

        mock_nats_mq_adapter._js.delete_stream.assert_called_once_with(self.consumer_queue.queue_name)
        assert result is None
