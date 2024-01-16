import asyncio
from unittest.mock import AsyncMock

import pytest
from nats.js.api import ConsumerConfig
from nats.js.errors import NotFoundError

from shared.adapters.nats_adapter import NatsKVAdapter, NatsMQAdapter, NatsKeys
from tests.conftest import (
    SUBSCRIBER_NAME,
    set_up_fake_js,
    set_up_fake_kv_store,
    kv_sub_info,
    SUBSCRIBER_INFO,
    MSG,
    MESSAGE,
    FLAT_MESSAGE_ENCODED,
    MQMESSAGE,
)


@pytest.fixture
def nats_kv_adapter() -> NatsKVAdapter:
    nats_kv_adapter = NatsKVAdapter()
    set_up_fake_js(nats_kv_adapter)
    set_up_fake_kv_store(nats_kv_adapter)
    nats_kv_adapter.nats = AsyncMock()
    return nats_kv_adapter


@pytest.fixture
def nats_mq_adapter() -> NatsMQAdapter:
    nats_mq_adapter = NatsMQAdapter()
    set_up_fake_js(nats_mq_adapter)
    nats_mq_adapter.nats = AsyncMock()
    nats_mq_adapter.message_queue.get = AsyncMock(return_value=MSG)
    nats_mq_adapter.message_queue.put = AsyncMock()
    return nats_mq_adapter


@pytest.fixture
def mock_fetch(nats_mq_adapter):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    nats_mq_adapter.js.pull_subscribe = AsyncMock(return_value=sub)
    return sub.fetch


@pytest.mark.anyio
class TestNatsKVAdapter:
    key = f"subscriber:{SUBSCRIBER_NAME}"

    async def test_connect(self, nats_kv_adapter):
        result = await nats_kv_adapter.connect()

        nats_kv_adapter.nats.connect.assert_called_once_with(["nats://localhost:4222"])
        nats_kv_adapter.js.create_key_value.assert_called_once_with(bucket="Pub_Sub_KV")
        assert result is None

    async def test_close(self, nats_kv_adapter):
        result = await nats_kv_adapter.close()

        nats_kv_adapter.nats.close.assert_called_once_with()
        assert result is None

    async def test_create_kv_store(self, nats_kv_adapter):
        result = await nats_kv_adapter.create_kv_store()

        nats_kv_adapter.js.create_key_value.assert_called_once_with(bucket="Pub_Sub_KV")
        assert result is None

    async def test_delete_kv_pair(self, nats_kv_adapter):
        result = await nats_kv_adapter.delete_kv_pair(self.key)

        nats_kv_adapter.kv_store.delete.assert_called_once_with(self.key)
        assert result is None

    async def test_get_value(self, nats_kv_adapter):
        result = await nats_kv_adapter.get_value(self.key)

        nats_kv_adapter.kv_store.get.assert_called_once_with(self.key)
        assert result == kv_sub_info

    async def test_get_value_by_unknown_key(self, nats_kv_adapter):
        result = await nats_kv_adapter.get_value("unknown")

        assert result is None

    async def test_put_value(self, nats_kv_adapter):
        result = await nats_kv_adapter.put_value(self.key, SUBSCRIBER_INFO)

        nats_kv_adapter.kv_store.put.assert_called_once_with(
            self.key, kv_sub_info.value
        )
        nats_kv_adapter.kv_store.delete.assert_not_called()
        assert result is None

    async def test_put_empty_value(self, nats_kv_adapter):
        result = await nats_kv_adapter.put_value(self.key, "")

        nats_kv_adapter.kv_store.delete.assert_called_once_with(self.key)
        nats_kv_adapter.kv_store.put.assert_not_called()
        assert result is None


@pytest.mark.anyio
class TestNatsMQAdapter:
    async def test_connect(self, nats_mq_adapter):
        result = await nats_mq_adapter.connect()

        nats_mq_adapter.nats.connect.assert_called_once_with(["nats://localhost:4222"])
        assert result is None

    async def test_close(self, nats_mq_adapter):
        result = await nats_mq_adapter.close()

        nats_mq_adapter.nats.close.assert_called_once_with()
        assert result is None

    async def test_add_message_new_stream(self, nats_mq_adapter):
        nats_mq_adapter.js.stream_info = AsyncMock(side_effect=NotFoundError)

        result = await nats_mq_adapter.add_message(SUBSCRIBER_NAME, MESSAGE)

        nats_mq_adapter.js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        nats_mq_adapter.js.add_stream.assert_called_once_with(
            name=NatsKeys.stream(SUBSCRIBER_NAME), subjects=[SUBSCRIBER_NAME]
        )
        nats_mq_adapter.js.add_consumer.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME),
            ConsumerConfig(durable_name=NatsKeys.durable_name(SUBSCRIBER_NAME)),
        )
        nats_mq_adapter.js.publish.assert_called_once_with(
            SUBSCRIBER_NAME,
            FLAT_MESSAGE_ENCODED,
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        assert result is None

    async def test_get_messages(self, nats_mq_adapter, mock_fetch):
        nats_mq_adapter.remove_message = AsyncMock()

        result = await nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=False
        )

        nats_mq_adapter.js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        nats_mq_adapter.js.pull_subscribe.assert_called_once_with(
            SUBSCRIBER_NAME,
            durable=f"durable_name:{SUBSCRIBER_NAME}",
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        mock_fetch.assert_called_once_with(1, 5)
        nats_mq_adapter.remove_message.assert_not_called()
        assert result == [MQMESSAGE]

    async def test_get_messages_with_removing(self, nats_mq_adapter, mock_fetch):
        nats_mq_adapter.remove_message = AsyncMock()

        result = await nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=True
        )

        nats_mq_adapter.js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        nats_mq_adapter.js.pull_subscribe.assert_called_once_with(
            SUBSCRIBER_NAME,
            durable=f"durable_name:{SUBSCRIBER_NAME}",
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        mock_fetch.assert_called_once_with(1, 5)
        nats_mq_adapter.remove_message.assert_called_once_with(MSG)
        assert result == [MQMESSAGE]

    async def test_get_messages_without_stream(self, nats_mq_adapter, mock_fetch):
        nats_mq_adapter.js.stream_info = AsyncMock(side_effect=NotFoundError)
        nats_mq_adapter.remove_message = AsyncMock()

        result = await nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=False
        )

        nats_mq_adapter.js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        nats_mq_adapter.js.pull_subscribe.assert_not_called()
        mock_fetch.assert_not_called()
        nats_mq_adapter.remove_message.assert_not_called()
        assert result == []

    async def test_get_messages_timeout_error(self, nats_mq_adapter):
        sub = AsyncMock()
        sub.fetch = AsyncMock(side_effect=asyncio.TimeoutError)
        nats_mq_adapter.js.pull_subscribe = AsyncMock(return_value=sub)
        nats_mq_adapter.remove_message = AsyncMock()

        result = await nats_mq_adapter.get_messages(
            SUBSCRIBER_NAME, timeout=5, count=1, pop=False
        )

        nats_mq_adapter.js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        nats_mq_adapter.js.pull_subscribe.assert_called_once_with(
            SUBSCRIBER_NAME,
            durable=f"durable_name:{SUBSCRIBER_NAME}",
            stream=NatsKeys.stream(SUBSCRIBER_NAME),
        )
        sub.fetch.assert_called_once_with(1, 5)
        nats_mq_adapter.remove_message.assert_not_called()
        assert result == []

    @pytest.mark.parametrize("message", [MQMESSAGE, MSG])
    async def test_remove_message_with_custom_message(self, nats_mq_adapter, message):
        result = await nats_mq_adapter.remove_message(message)

        MSG.ack.assert_called_with()
        assert result is None

    async def test_delete_stream(self, nats_mq_adapter):
        result = await nats_mq_adapter.delete_stream(SUBSCRIBER_NAME)

        nats_mq_adapter.js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        nats_mq_adapter.js.delete_stream.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        assert result is None

    async def test_delete_stream_not_found(self, nats_mq_adapter):
        nats_mq_adapter.js.stream_info = AsyncMock(side_effect=NotFoundError)

        result = await nats_mq_adapter.delete_stream(SUBSCRIBER_NAME)

        nats_mq_adapter.js.stream_info.assert_called_once_with(
            NatsKeys.stream(SUBSCRIBER_NAME)
        )
        nats_mq_adapter.js.delete_stream.assert_not_called()
        assert result is None

    async def test_cb(self, nats_mq_adapter):
        result = await nats_mq_adapter.cb(MSG)

        nats_mq_adapter.message_queue.put.assert_called_once_with(MSG)
        assert result is None

    async def test_subscribe_to_queue(self, nats_mq_adapter):
        result = await nats_mq_adapter.subscribe_to_queue(SUBSCRIBER_NAME)

        nats_mq_adapter.nats.subscribe.assert_called_once_with(
            SUBSCRIBER_NAME, cb=nats_mq_adapter.cb
        )
        assert result is None

    async def test_wait_for_event(self, nats_mq_adapter):
        result = await nats_mq_adapter.wait_for_event()

        nats_mq_adapter.message_queue.get.assert_called_once_with()
        assert result == MSG
