# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call
import pytest

from shared.models.subscription import Bucket
from tests.conftest import (
    SUBSCRIPTION_INFO,
    SUBSCRIPTION_NAME,
    REALMS_TOPICS_STR,
)
from consumer.subscriptions.service.subscription import SubscriptionService

from shared.models import FillQueueStatus


@pytest.fixture
def sub_service() -> SubscriptionService:
    return SubscriptionService(AsyncMock())


@pytest.mark.anyio
class TestSubscriptionService:
    async def test_get_subscription_not_found(self, sub_service):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        assert "Subscription was not found." == str(e.value)

    async def test_get_subscription_queue_status_with_no_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        assert "Subscription was not found." == str(e.value)

    async def test_get_subscription_queue_status_with_subscriptions(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        assert result == FillQueueStatus.done

    async def test_set_subscription_queue_status_with_no_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.set_subscription_queue_status(
                SUBSCRIPTION_NAME, FillQueueStatus.pending
            )

        sub_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        sub_service._port.put_value.assert_not_called()
        assert "Subscription was not found." == str(e.value)

    async def test_set_subscription_queue_status_with_subscriptions(
        self, sub_service: SubscriptionService
    ):
        sub_info = deepcopy(SUBSCRIPTION_INFO)
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.set_subscription_queue_status(
            SUBSCRIPTION_NAME, FillQueueStatus.pending
        )
        sub_info["prefill_queue_status"] = "pending"

        sub_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        sub_service._port.put_value.assert_called_once_with(
            SUBSCRIPTION_NAME, sub_info, Bucket.subscriptions
        )
        assert result is None

    async def test_delete_subscription_with_no_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        sub_service._port.put_value.assert_not_called()
        assert "Subscription was not found." == str(e.value)

    async def test_delete_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIPTION_NAME])

        await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(
            SUBSCRIPTION_NAME, Bucket.subscriptions
        )
        sub_service._port.get_list_value.assert_called_once_with(
            REALMS_TOPICS_STR, Bucket.subscriptions
        )
        sub_service._port.put_list_value.assert_called_once_with(
            REALMS_TOPICS_STR, [], Bucket.subscriptions
        )
        sub_service._port.delete_kv_pair.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, Bucket.credentials),
                call(SUBSCRIPTION_NAME, Bucket.subscriptions),
            ]
        )
