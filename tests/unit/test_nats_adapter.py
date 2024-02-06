# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
from unittest.mock import AsyncMock

import pytest
from nats.js.errors import NotFoundError

from shared.adapters.nats_adapter import NatsKeys
from tests.conftest import (
    SUBSCRIBER_NAME,
    kv_sub_info,
    SUBSCRIBER_INFO,
    MSG,
    MESSAGE,
    MQMESSAGE,
    MockNatsMQAdapter,
    MockNatsKVAdapter,
    FLAT_MESSAGE_ENCODED,
)


@pytest.fixture
def mock_nats_mq_adapter() -> MockNatsMQAdapter:
    return MockNatsMQAdapter()


@pytest.fixture
def mock_nats_kv_adapter() -> MockNatsKVAdapter:
    return MockNatsKVAdapter()


@pytest.fixture
def mock_fetch(mock_nats_mq_adapter):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    mock_nats_mq_adapter._js.pull_subscribe = AsyncMock(return_value=sub)
    return sub.fetch


@pytest.mark.anyio
class TestNatsKVAdapter:
    key = f"subscriber:{SUBSCRIBER_NAME}"

    async def test_connect(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.connect()

        mock_nats_kv_adapter._nats.connect.assert_called_once_with(
            ["nats://localhost:4222"]
        )
        mock_nats_kv_adapter._js.create_key_value.assert_called_once()
        assert result is None

    async def test_close(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.close()

        mock_nats_kv_adapter._nats.close.assert_called_once_with()
        assert result is None

    async def test_create_kv_store(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.create_kv_store()

        mock_nats_kv_adapter._js.create_key_value.assert_called_once_with(
            bucket="Pub_Sub_KV"
        )
        assert result is None

    async def test_delete_kv_pair(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.delete_kv_pair(self.key)

        mock_nats_kv_adapter._kv_store.delete.assert_called_once_with(self.key)
        assert result is None

    async def test_get_value(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.get_value(self.key)

        assert result == kv_sub_info

    async def test_get_value_by_unknown_key(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.get_value("unknown")

        assert result is None

    async def test_put_value(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.put_value(self.key, SUBSCRIBER_INFO)

        mock_nats_kv_adapter._kv_store.put.assert_called_once_with(
            self.key, kv_sub_info.value
        )
        mock_nats_kv_adapter._kv_store.delete.assert_not_called()
        assert result is None

    async def test_put_empty_value(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.put_value(self.key, "")

        mock_nats_kv_adapter._kv_store.delete.assert_called_once_with(self.key)
        mock_nats_kv_adapter._kv_store.put.assert_not_called()
        assert result is None


@pytest.mark.anyio
class TestNatsMQAdapter:
    async def test_connect(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.connect()

        mock_nats_mq_adapter._nats.connect.assert_called_once_with(
            ["nats://localhost:4222"]
        )
        assert result is None

    async def test_close(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.close()

        mock_nats_mq_adapter._nats.close.assert_called_once_with()
        assert result is None

    async def test_add_message_new_stream(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.add_message(SUBSCRIBER_NAME, MESSAGE)

        mock_nats_mq_adapter._js.publish.assert_called_once_with(
            SUBSCRIBER_NAME,
            FLAT_MESSAGE_ENCODED,
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        assert result is None

    async def test_get_messages(self, mock_nats_mq_adapter, mock_fetch):
        mock_nats_mq_adapter.remove_message = AsyncMock()

        result = await mock_nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=False
        )

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            SUBSCRIBER_NAME,
            durable=f"durable_name:{SUBSCRIBER_NAME}",
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        mock_fetch.assert_called_once_with(1, 5)
        mock_nats_mq_adapter.remove_message.assert_not_called()
        assert result == [MQMESSAGE]

    async def test_get_messages_with_removing(self, mock_nats_mq_adapter, mock_fetch):
        mock_nats_mq_adapter.remove_message = AsyncMock()

        result = await mock_nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=True
        )

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            SUBSCRIBER_NAME,
            durable=f"durable_name:{SUBSCRIBER_NAME}",
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        mock_fetch.assert_called_once_with(1, 5)
        mock_nats_mq_adapter.remove_message.assert_called_once_with(MSG)
        assert result == [MQMESSAGE]

    async def test_get_messages_without_stream(self, mock_nats_mq_adapter, mock_fetch):
        mock_nats_mq_adapter._js.stream_info = AsyncMock(side_effect=NotFoundError)
        mock_nats_mq_adapter.remove_message = AsyncMock()

        result = await mock_nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=False
        )

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_not_called()
        mock_fetch.assert_not_called()
        mock_nats_mq_adapter.remove_message.assert_not_called()
        assert result == []

    async def test_get_messages_timeout_error(self, mock_nats_mq_adapter):
        sub = AsyncMock()
        sub.fetch = AsyncMock(side_effect=asyncio.TimeoutError)
        mock_nats_mq_adapter._js.pull_subscribe = AsyncMock(return_value=sub)
        mock_nats_mq_adapter.remove_message = AsyncMock()

        result = await mock_nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=False
        )

        mock_nats_mq_adapter._js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        mock_nats_mq_adapter._js.pull_subscribe.assert_called_once_with(
            SUBSCRIBER_NAME,
            durable=f"durable_name:{SUBSCRIBER_NAME}",
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        sub.fetch.assert_called_once_with(1, 5)
        mock_nats_mq_adapter.remove_message.assert_not_called()
        assert result == []

    @pytest.mark.parametrize("message", [MQMESSAGE, MSG])
    async def test_remove_message_with_custom_message(
        self, mock_nats_mq_adapter, message
    ):
        result = await mock_nats_mq_adapter.remove_message(message)

        MSG.ack.assert_called_with()
        assert result is None

    async def test_delete_stream(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.delete_stream(SUBSCRIBER_NAME)

        mock_nats_mq_adapter._js.delete_stream.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        assert result is None

    async def test_delete_stream_not_found(self, mock_nats_mq_adapter):
        mock_nats_mq_adapter._js.delete_stream = AsyncMock(side_effect=NotFoundError)

        result = await mock_nats_mq_adapter.delete_stream(SUBSCRIBER_NAME)

        mock_nats_mq_adapter._js.delete_stream.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        assert result is None

    async def test_cb(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.cb(MSG)

        mock_nats_mq_adapter._message_queue.put.assert_called_once_with(MSG)
        assert result is None

    async def test_subscribe_to_queue(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.subscribe_to_queue(
            "incoming", "dispatcher-service"
        )

        mock_nats_mq_adapter._js.subscribe.assert_called_once_with(
            "incoming",
            cb=mock_nats_mq_adapter.cb,
            durable=NatsKeys.durable_name("incoming"),
            manual_ack=True,
        )
        assert result is None

    async def test_wait_for_event(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.wait_for_event()

        assert result == MQMESSAGE
