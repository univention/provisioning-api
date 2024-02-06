# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call
import pytest

from tests.conftest import (
    SUBSCRIPTION_INFO,
    SUBSCRIPTION_NAME,
    REALMS_TOPICS_STR,
    REALMS_TOPICS,
)
from consumer.subscriptions.service.subscription import (
    SubscriptionService,
    SUBSCRIPTIONS,
)
from shared.models import Subscription, NewSubscription, FillQueueStatus


@pytest.fixture
def sub_service() -> SubscriptionService:
    return SubscriptionService(AsyncMock())


@pytest.mark.anyio
class TestSubscriptionService:
    new_subscription = NewSubscription(
        name=SUBSCRIPTION_NAME,
        realms_topics=REALMS_TOPICS,
        request_prefill=True,
    )

    async def test_get_subscriptions(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIPTION_NAME])
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        subscription = Subscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=[REALMS_TOPICS_STR],
            request_prefill=True,
            prefill_queue_status="done",
        )

        result = await sub_service.get_subscriptions()

        sub_service._port.get_list_value.assert_called_once_with(SUBSCRIPTIONS)
        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result == [subscription]

    async def test_get_subscriptions_empty_result(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[])

        result = await sub_service.get_subscriptions()

        sub_service._port.get_list_value.assert_called_once_with(SUBSCRIPTIONS)
        assert result == []

    async def test_get_subscription_not_found(self, sub_service):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        assert "Subscription was not found." == str(e.value)

    async def test_create_subscription_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        with pytest.raises(ValueError) as e:
            await sub_service.create_subscription(self.new_subscription)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        sub_service._port.put_value.assert_not_called()
        assert "Subscription with the given name already exists" == str(e.value)

    async def test_add_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.get_str_value = AsyncMock(side_effect=[None, None])
        sub_service._port.create_stream = AsyncMock()
        sub_service._port.create_consumer = AsyncMock()

        await sub_service.create_subscription(self.new_subscription)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        sub_service._port.get_str_value.assert_has_calls(
            [call(SUBSCRIPTIONS), call("udm:groups/group")]
        )
        sub_service._port.put_value.assert_has_calls(
            [
                call(SUBSCRIPTIONS, SUBSCRIPTION_NAME),
                call("udm:groups/group", SUBSCRIPTION_NAME),
            ]
        )

    async def test_get_subscription_queue_status_with_no_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        assert "Subscription was not found." == str(e.value)

    async def test_get_subscription_queue_status_with_subscriptions(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        assert result == FillQueueStatus.done

    async def test_set_subscription_queue_status_with_no_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.set_subscription_queue_status(
                SUBSCRIPTION_NAME, FillQueueStatus.pending
            )

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
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

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        sub_service._port.put_value.assert_called_once_with(SUBSCRIPTION_NAME, sub_info)
        assert result is None

    async def test_delete_subscription_with_no_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        sub_service._port.put_value.assert_not_called()
        assert "Subscription was not found." == str(e.value)

    async def test_delete_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service._port.get_list_value = AsyncMock(
            side_effect=[[SUBSCRIPTION_NAME], [SUBSCRIPTION_NAME]]
        )

        await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME)
        sub_service._port.get_list_value.assert_has_calls(
            [call(REALMS_TOPICS_STR), call(SUBSCRIPTIONS)]
        )
        sub_service._port.put_list_value.assert_has_calls(
            [call(REALMS_TOPICS_STR, []), call(SUBSCRIPTIONS, [])]
        )
