# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from contextlib import nullcontext
from unittest.mock import call

try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock

import pytest
from nats.js.errors import BucketNotFoundError
from test_helpers.mock_data import SUBSCRIPTION_NAME, SUBSCRIPTION_INFO_dumpable

from univention.provisioning.backends.key_value_db import BucketName, UpdateConflict
from univention.provisioning.backends.mocks import FakeKvStore, MockNatsKVAdapter, kv_sub_info


@pytest.fixture
def mock_kv():
    mock_kv = AsyncMock()
    mock_kv._fake_kv = FakeKvStore(BucketName.subscriptions)
    mock_kv.get = AsyncMock(side_effect=mock_kv._fake_kv.get)
    mock_kv.put = AsyncMock(side_effect=mock_kv._fake_kv.put)
    mock_kv.update = AsyncMock(side_effect=mock_kv._fake_kv.update)
    return mock_kv


@pytest.fixture
def mock_nats_kv_adapter(mock_kv, nats_credentials) -> MockNatsKVAdapter:
    mock_nats = MockNatsKVAdapter(
        server="nats://localhost:4222", user=nats_credentials["username"], password=nats_credentials["password"]
    )
    mock_nats._js.key_value = AsyncMock(return_value=mock_kv)
    return mock_nats


@pytest.mark.anyio
class TestNatsKVAdapter:
    async def test_connect(self, mock_nats_kv_adapter, nats_credentials):
        mock_nats_kv_adapter._js.key_value = AsyncMock(side_effect=BucketNotFoundError)

        result = await mock_nats_kv_adapter.init(buckets=[BucketName.subscriptions])

        mock_nats_kv_adapter._nats.connect.assert_called_once_with(
            servers="nats://localhost:4222",
            user=nats_credentials["username"],
            password=nats_credentials["password"],
            max_reconnect_attempts=1,
        )
        mock_nats_kv_adapter._js.create_key_value.assert_called_once_with(bucket=BucketName.subscriptions)
        assert result is None

    async def test_close(self, mock_nats_kv_adapter):
        result = await mock_nats_kv_adapter.close()

        mock_nats_kv_adapter._nats.close.assert_called_once_with()
        assert result is None

    async def test_create_kv_store(self, mock_nats_kv_adapter):
        mock_nats_kv_adapter._js.key_value = AsyncMock(side_effect=BucketNotFoundError)

        result = await mock_nats_kv_adapter.create_kv_store(BucketName.subscriptions)

        mock_nats_kv_adapter._js.create_key_value.assert_called_once_with(bucket=BucketName.subscriptions)
        assert result is None

    async def test_delete_kv_pair(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.delete_kv_pair(SUBSCRIPTION_NAME, BucketName.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(BucketName.subscriptions)
        mock_kv.delete.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result is None

    async def test_get_value(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.get_value(SUBSCRIPTION_NAME, BucketName.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(BucketName.subscriptions)
        mock_kv.get.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result == json.dumps(SUBSCRIPTION_INFO_dumpable)

    async def test_get_value_with_revision(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.get_value_with_revision(SUBSCRIPTION_NAME, BucketName.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(BucketName.subscriptions)
        mock_kv.get.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result == (json.dumps(SUBSCRIPTION_INFO_dumpable), 12)

    async def test_get_value_by_unknown_key(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.get_value("unknown", BucketName.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(BucketName.subscriptions)
        mock_kv.get.assert_called_once_with("unknown")
        assert result is None

    async def test_put_value(self, mock_nats_kv_adapter, mock_kv):
        result = await mock_nats_kv_adapter.put_value(
            "test_put_value", SUBSCRIPTION_INFO_dumpable, BucketName.subscriptions
        )

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(BucketName.subscriptions)
        mock_kv.delete.assert_not_called()
        mock_kv.put.assert_called_once_with("test_put_value", kv_sub_info.value)
        assert result is None

    @pytest.mark.parametrize("revision,expectation", ((12, nullcontext(None)), (13, pytest.raises(UpdateConflict))))
    async def test_put_value_with_revision(self, mock_nats_kv_adapter, mock_kv, revision, expectation):
        with expectation as exc_info:
            result = await mock_nats_kv_adapter.put_value(
                SUBSCRIPTION_NAME, SUBSCRIPTION_INFO_dumpable, BucketName.subscriptions, revision
            )
        if exc_info:
            assert exc_info.type is UpdateConflict
            return

        mock_nats_kv_adapter._js.key_value.assert_called_once_with(BucketName.subscriptions)
        mock_kv.delete.assert_not_called()
        mock_kv.put.assert_not_called()
        mock_kv.update.assert_called_once_with(SUBSCRIPTION_NAME, kv_sub_info.value, revision)
        assert result is None

    async def test_put_empty_value(self, mock_nats_kv_adapter, mock_kv):
        await mock_nats_kv_adapter.put_value(
            "test_put_empty_value", SUBSCRIPTION_INFO_dumpable, BucketName.subscriptions
        )
        assert "test_put_empty_value" in mock_kv._fake_kv._values
        mock_kv.put.reset_mock()

        result = await mock_nats_kv_adapter.put_value("test_put_empty_value", "", BucketName.subscriptions)

        mock_nats_kv_adapter._js.key_value.assert_has_calls(
            [call(BucketName.subscriptions), call(BucketName.subscriptions)]
        )
        mock_kv.delete.assert_called_once_with("test_put_empty_value")
        mock_kv.put.assert_not_called()
        assert result is None
