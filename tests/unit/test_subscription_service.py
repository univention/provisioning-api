# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call
import pytest

from tests.conftest import (
    SUBSCRIBER_INFO,
    SUBSCRIPTION_NAME,
    REALM,
    TOPIC,
)
from consumer.subscriptions.service.subscription import (
    SubscriptionService,
    SubscriptionKeys,
)
from shared.models import Subscription, NewSubscription, FillQueueStatus


@pytest.fixture
def sub_service() -> SubscriptionService:
    return SubscriptionService(AsyncMock())


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
class TestSubscriptionService:
    new_subscriber = NewSubscription(
        name=SUBSCRIPTION_NAME,
        realm=REALM,
        topic=TOPIC,
        request_prefill=True,
    )
    subscription = SubscriptionKeys.subscription(SUBSCRIPTION_NAME)

    async def test_get_subscribers(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIPTION_NAME])
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)
        subscriber = Subscription(
            name=SUBSCRIPTION_NAME,
            realm=REALM,
            topic=TOPIC,
            request_prefill=True,
            prefill_queue_status="done",
        )

        result = await sub_service.get_subscribers(None)

        sub_service._port.get_list_value.assert_called_once_with(
            SubscriptionKeys.subscribers
        )
        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        assert result == [subscriber]

    async def test_get_subscribers_empty_result(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[])

        result = await sub_service.get_subscribers(None)

        sub_service._port.get_list_value.assert_called_once_with(
            SubscriptionKeys.subscribers
        )
        assert result == []

    async def test_get_subscriber_not_found(self, sub_service):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_info(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        assert "Subscription not found." == str(e.value)

    async def test_create_subscription_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        with pytest.raises(ValueError) as e:
            await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        sub_service._port.put_value.assert_not_called()
        assert "The subscription with the given name already exists" == str(e.value)

    async def test_add_subscriber(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.get_str_value = AsyncMock(side_effect=[None, None])

        await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        sub_service._port.get_str_value.assert_has_calls(
            [call(SubscriptionKeys.subscribers), call("udm:users/user")]
        )
        sub_service._port.put_value.assert_has_calls(
            [
                call(SubscriptionKeys.subscribers, SUBSCRIPTION_NAME),
                call("udm:users/user", SUBSCRIPTION_NAME),
            ]
        )

    async def test_get_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        assert "Subscription not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        result = await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        assert result == FillQueueStatus.done

    async def test_set_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.set_subscription_queue_status(
                SUBSCRIPTION_NAME, FillQueueStatus.pending
            )

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        sub_service._port.put_value.assert_not_called()
        assert "Subscription not found." == str(e.value)

    async def test_set_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        result = await sub_service.set_subscription_queue_status(
            SUBSCRIPTION_NAME, FillQueueStatus.pending
        )
        sub_info["prefill_queue_status"] = "pending"

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        sub_service._port.put_value.assert_called_once_with(self.subscription, sub_info)
        assert result is None

    async def test_cancel_subscription_with_no_existing_realm_topic(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(SUBSCRIPTION_NAME, "abc", "def")

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        sub_service._port.put_value.assert_not_called()
        assert "The subscription with the given name does not exist" == str(e.value)

    async def test_cancel_subscription_with_no_existing_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(SUBSCRIPTION_NAME, "abc", "def")

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        sub_service._port.put_value.assert_not_called()
        assert "Subscription not found." == str(e.value)

    async def test_cancel_subscription(self, sub_service: SubscriptionService):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_service._port.get_dict_value = AsyncMock(return_value=sub_info)
        sub_service._port.get_list_value = AsyncMock(
            side_effect=[[SUBSCRIPTION_NAME], [SUBSCRIPTION_NAME]]
        )

        await sub_service.cancel_subscription(SUBSCRIPTION_NAME, "udm", "users/user")

        sub_service._port.get_dict_value.assert_called_once_with(self.subscription)
        sub_service._port.get_list_value.assert_has_calls(
            [call("udm:users/user"), call(SubscriptionKeys.subscribers)]
        )
        sub_service._port.put_list_value.assert_has_calls(
            [call("udm:users/user", []), call("subscriptions", [])]
        )
        sub_service._port.delete_kv_pair.assert_called_once_with(self.subscription)
        sub_service._port.delete_stream.assert_called_once_with(SUBSCRIPTION_NAME)
        sub_service._port.delete_consumer.assert_called_once_with(SUBSCRIPTION_NAME)
