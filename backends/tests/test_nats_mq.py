# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from nats.js.errors import NotFoundError

from univention.provisioning.backends.mocks import MockNatsMQAdapter
from univention.provisioning.backends.nats_mq import NatsKeys
from univention.provisioning.testing.mock_data import (
    FLAT_MESSAGE_ENCODED,
    MESSAGE,
    MQMESSAGE,
    MSG,
    NATS_SERVER,
    PROVISIONING_MESSAGE,
    SUBSCRIPTION_NAME,
)

CREDENTIALS = {"username": "dev-user", "password": "dev-password"}


@pytest.fixture
def mock_nats_mq_adapter() -> MockNatsMQAdapter:
    return MockNatsMQAdapter()


@pytest.fixture
def mock_fetch(mock_nats_mq_adapter):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    mock_nats_mq_adapter._js.pull_subscribe = AsyncMock(return_value=sub)
    return sub.fetch


@pytest.mark.anyio
class TestNatsMQAdapter:
    subject = "subject"

    async def test_connect(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.connect(
            server=NATS_SERVER, user=CREDENTIALS["username"], password=CREDENTIALS["password"]
        )

        mock_nats_mq_adapter._nats.connect.assert_called_once_with(
            servers=NATS_SERVER,
            user=CREDENTIALS["username"],
            password=CREDENTIALS["password"],
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
        result = await mock_nats_mq_adapter.add_message(SUBSCRIPTION_NAME, self.subject, MESSAGE)

        mock_nats_mq_adapter._js.publish.assert_called_once_with(
            self.subject,
            FLAT_MESSAGE_ENCODED,
            stream=NatsKeys.stream(SUBSCRIPTION_NAME),
        )
        assert result is None

    async def test_get_messages(self, mock_nats_mq_adapter, mock_fetch):
        consumer_mock = Mock()
        mock_nats_mq_adapter.delete_message = AsyncMock()
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(return_value=consumer_mock)

        result = await mock_nats_mq_adapter.get_message(SUBSCRIPTION_NAME, self.subject, timeout=5, pop=False)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME))
        mock_nats_mq_adapter._js.consumer_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIPTION_NAME), NatsKeys.durable_name(SUBSCRIPTION_NAME)
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            self.subject,
            durable=f"durable_name:{SUBSCRIPTION_NAME}",
            stream=NatsKeys.stream(SUBSCRIPTION_NAME),
            config=consumer_mock,
        )
        mock_fetch.assert_called_once_with(1, 5)
        mock_nats_mq_adapter.delete_message.assert_not_called()
        assert result == PROVISIONING_MESSAGE

    async def test_get_messages_with_removing(self, mock_nats_mq_adapter, mock_fetch):
        consumer_mock = Mock()
        mock_nats_mq_adapter.delete_message = AsyncMock()
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(return_value=consumer_mock)

        result = await mock_nats_mq_adapter.get_message(SUBSCRIPTION_NAME, self.subject, timeout=5, pop=True)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME))
        mock_nats_mq_adapter._js.consumer_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIPTION_NAME), NatsKeys.durable_name(SUBSCRIPTION_NAME)
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            self.subject,
            durable=f"durable_name:{SUBSCRIPTION_NAME}",
            stream=NatsKeys.stream(SUBSCRIPTION_NAME),
            config=consumer_mock,
        )
        mock_fetch.assert_called_once_with(1, 5)
        MSG.ack.assert_called_with()
        assert result == PROVISIONING_MESSAGE

    async def test_get_messages_without_stream(self, mock_nats_mq_adapter, mock_fetch):
        mock_nats_mq_adapter._js.stream_info = AsyncMock(side_effect=NotFoundError)
        mock_nats_mq_adapter.delete_message = AsyncMock()

        result = await mock_nats_mq_adapter.get_message(SUBSCRIPTION_NAME, self.subject, timeout=5, pop=False)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME))
        mock_nats_mq_adapter._js.pull_subscribe.assert_not_called()
        mock_nats_mq_adapter._js.consumer_info.assert_not_called()
        mock_fetch.assert_not_called()
        mock_nats_mq_adapter.delete_message.assert_not_called()
        assert result is None

    async def test_get_messages_timeout_error(self, mock_nats_mq_adapter):
        sub = AsyncMock()
        consumer_mock = Mock()
        sub.fetch = AsyncMock(side_effect=asyncio.TimeoutError)
        mock_nats_mq_adapter._js.pull_subscribe = AsyncMock(return_value=sub)
        mock_nats_mq_adapter.delete_message = AsyncMock()
        mock_nats_mq_adapter._js.consumer_info = AsyncMock(return_value=consumer_mock)

        result = await mock_nats_mq_adapter.get_message(SUBSCRIPTION_NAME, self.subject, timeout=5, pop=False)

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME))
        mock_nats_mq_adapter._js.consumer_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIPTION_NAME), NatsKeys.durable_name(SUBSCRIPTION_NAME)
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            self.subject,
            durable=NatsKeys.durable_name(SUBSCRIPTION_NAME),
            stream=NatsKeys.stream(SUBSCRIPTION_NAME),
            config=consumer_mock,
        )
        sub.fetch.assert_called_once_with(1, 5)
        mock_nats_mq_adapter.delete_message.assert_not_called()
        assert result is None

    async def test_delete_message(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.delete_message(SUBSCRIPTION_NAME, 1)

        mock_nats_mq_adapter._js.get_msg.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME), 1)
        mock_nats_mq_adapter._js.delete_msg.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME), 1)
        assert result is None

    async def test_delete_message_no_message(self, mock_nats_mq_adapter):
        error = NotFoundError()
        error.description = "Message not found"
        mock_nats_mq_adapter._js.get_msg = AsyncMock(side_effect=error)

        with pytest.raises(ValueError, match="Message not found"):
            await mock_nats_mq_adapter.delete_message(SUBSCRIPTION_NAME, 1)

        mock_nats_mq_adapter._js.get_msg.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME), 1)
        mock_nats_mq_adapter._js.delete_msg.assert_not_called()

    async def test_delete_stream(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.delete_stream(SUBSCRIPTION_NAME)

        mock_nats_mq_adapter._js.delete_stream.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME))
        assert result is None

    async def test_delete_stream_not_found(self, mock_nats_mq_adapter):
        mock_nats_mq_adapter._js.delete_stream = AsyncMock(side_effect=NotFoundError)

        result = await mock_nats_mq_adapter.delete_stream(SUBSCRIPTION_NAME)

        mock_nats_mq_adapter._js.delete_stream.assert_called_once_with(NatsKeys.stream(SUBSCRIPTION_NAME))
        assert result is None

    async def test_cb(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.cb(MSG)

        mock_nats_mq_adapter._message_queue.put.assert_called_once_with(MSG)
        assert result is None

    async def test_subscribe_to_queue(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.subscribe_to_queue("incoming", "dispatcher-service")

        mock_nats_mq_adapter._js.subscribe.assert_called_once_with(
            "incoming",
            cb=mock_nats_mq_adapter.cb,
            durable=NatsKeys.durable_name("incoming"),
            stream=NatsKeys.stream("incoming"),
            manual_ack=True,
        )
        assert result is None

    async def test_wait_for_event(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.wait_for_event()

        assert result == MQMESSAGE
