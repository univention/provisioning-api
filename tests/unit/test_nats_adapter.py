# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import json
from contextlib import nullcontext
from unittest.mock import AsyncMock, Mock, call

import pytest
from nats.js.errors import BucketNotFoundError, NotFoundError

from server.adapters.nats_adapter import NatsKeys, UpdateConflict
from univention.provisioning.models import Bucket

from ..mock_data import (
    CREDENTIALS,
    FLAT_MESSAGE_ENCODED,
    MESSAGE,
    MQMESSAGE,
    MSG,
    NATS_SERVER,
    PROVISIONING_MESSAGE,
    SUBSCRIPTION_NAME,
    SUBSCRIPTION_INFO_dumpable,
    kv_sub_info,
)
from ..mocks import FakeKvStore, MockNatsKVAdapter, MockNatsMQAdapter


@pytest.fixture
def mock_nats_mq_adapter() -> MockNatsMQAdapter:
    return MockNatsMQAdapter()


@pytest.fixture
def mock_kv():
    mock_kv = AsyncMock()
    mock_kv._fake_kv = FakeKvStore(Bucket.subscriptions)
    mock_kv.get = AsyncMock(side_effect=mock_kv._fake_kv.get)
    mock_kv.put = AsyncMock(side_effect=mock_kv._fake_kv.put)
    mock_kv.update = AsyncMock(side_effect=mock_kv._fake_kv.update)
    return mock_kv


@pytest.fixture
def mock_nats_kv_adapter(mock_kv) -> MockNatsKVAdapter:
    mock_nats = MockNatsKVAdapter()
    mock_nats._js.key_value = AsyncMock(return_value=mock_kv)
    return mock_nats


@pytest.fixture
def mock_fetch(mock_nats_mq_adapter):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    mock_nats_mq_adapter._js.pull_subscribe = AsyncMock(return_value=sub)
    return sub.fetch


@pytest.mark.anyio
class TestNatsKVAdapter:
    async def test_connect(self, mock_nats_kv_adapter):
        mock_nats_kv_adapter._js.key_value = AsyncMock(side_effect=BucketNotFoundError)

        result = await mock_nats_kv_adapter.init(
            server="nats://localhost:4222",
            user=CREDENTIALS.username,
            password=CREDENTIALS.password,
            buckets=[Bucket.subscriptions],
        )

        mock_nats_kv_adapter._nats.connect.assert_called_once_with(
            servers="nats://localhost:4222",
            user=CREDENTIALS.username,
            password=CREDENTIALS.password,
            max_reconnect_attempts=1,
        )
        mock_nats_kv_adapter._js.create_key_value.assert_called_once_with(bucket=Bucket.subscriptions)
        assert result is None

    async def test_close(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.close()

        mock_nats_kv_adapter._nats.close.assert_called_once_with()
        assert result is None

    async def test_create_kv_store(self, mock_nats_kv_adapter):
        mock_nats_kv_adapter._js.key_value = AsyncMock(side_effect=BucketNotFoundError)

        result = await mock_nats_kv_adapter.create_kv_store(Bucket.subscriptions)

        mock_nats_kv_adapter._js.create_key_value.assert_called_once_with(bucket=Bucket.subscriptions)
        assert result is None

    async def test_delete_kv_pair(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.delete_kv_pair(SUBSCRIPTION_NAME, Bucket.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(Bucket.subscriptions)
        mock_kv.delete.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result is None

    async def test_get_value(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.get_value(SUBSCRIPTION_NAME, Bucket.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(Bucket.subscriptions)
        mock_kv.get.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result == json.dumps(SUBSCRIPTION_INFO_dumpable)

    async def test_get_value_with_revision(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.get_value_with_revision(SUBSCRIPTION_NAME, Bucket.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(Bucket.subscriptions)
        mock_kv.get.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result == (json.dumps(SUBSCRIPTION_INFO_dumpable), 12)

    async def test_get_value_by_unknown_key(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.get_value("unknown", Bucket.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(Bucket.subscriptions)
        mock_kv.get.assert_called_once_with("unknown")
        assert result is None

    async def test_put_value(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.put_value(
            "test_put_value", SUBSCRIPTION_INFO_dumpable, Bucket.subscriptions
        )

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(Bucket.subscriptions)
        mock_kv.delete.assert_not_called()
        mock_kv.put.assert_called_once_with("test_put_value", kv_sub_info.value)
        assert result is None

    @pytest.mark.parametrize("revision,expectation", ((12, nullcontext(None)), (13, pytest.raises(UpdateConflict))))
    async def test_put_value_with_revision(self, mock_nats_kv_adapter, mock_kv, revision, expectation):
        with expectation as exc_info:
            result = await mock_nats_kv_adapter.put_value(
                SUBSCRIPTION_NAME, SUBSCRIPTION_INFO_dumpable, Bucket.subscriptions, revision
            )
        if exc_info:
            assert exc_info.type is UpdateConflict
            return

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(Bucket.subscriptions)
        mock_kv.delete.assert_not_called()
        mock_kv.put.assert_not_called()
        mock_kv.update.assert_called_once_with(SUBSCRIPTION_NAME, kv_sub_info.value, revision)
        assert result is None

    async def test_put_empty_value(self, mock_nats_kv_adapter, mock_kv):
        await mock_nats_kv_adapter.put_value("test_put_empty_value", SUBSCRIPTION_INFO_dumpable, Bucket.subscriptions)
        assert "test_put_empty_value" in mock_kv._fake_kv._values
        mock_kv.put.reset_mock()

        result = await mock_nats_kv_adapter.put_value("test_put_empty_value", "", Bucket.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_has_calls([call(Bucket.subscriptions), call(Bucket.subscriptions)])
        mock_kv.delete.assert_called_once_with("test_put_empty_value")
        mock_kv.put.assert_not_called()
        assert result is None


@pytest.mark.anyio
class TestNatsMQAdapter:
    subject = "subject"

    async def test_connect(self, mock_nats_mq_adapter):
        result = await mock_nats_mq_adapter.connect(
            server=NATS_SERVER, user=CREDENTIALS.username, password=CREDENTIALS.password
        )

        mock_nats_mq_adapter._nats.connect.assert_called_once_with(
            servers=NATS_SERVER,
            user=CREDENTIALS.username,
            password=CREDENTIALS.password,
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
