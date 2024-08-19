# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call

import pytest
from fastapi import HTTPException

from server.services.subscriptions import SubscriptionService
from univention.provisioning.models import FillQueueStatus, NewSubscription
from univention.provisioning.models.subscription import Bucket, Subscription

from tests.conftest import (
    CONSUMER_HASHED_PASSWORD,
    GROUPS_REALMS_TOPICS,
    GROUPS_TOPIC,
    REALM,
    REALMS_TOPICS_STR,
    SUBSCRIPTION_INFO,
    SUBSCRIPTION_NAME,
    USERS_TOPIC,
)


@pytest.fixture
def sub_service() -> SubscriptionService:
    return SubscriptionService(AsyncMock())


@pytest.mark.anyio
class TestSubscriptionService:
    new_subscription = NewSubscription(
        name=SUBSCRIPTION_NAME,
        realms_topics=GROUPS_REALMS_TOPICS,
        request_prefill=True,
        password="password",
    )

    async def test_get_subscriptions(self, sub_service: SubscriptionService):
        sub_service._port.get_bucket_keys = AsyncMock(return_value=[SUBSCRIPTION_NAME])
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        subscription = Subscription(
            name=SUBSCRIPTION_NAME,
            realms_topics=[REALMS_TOPICS_STR],
            request_prefill=True,
            prefill_queue_status="done",
        )

        result = await sub_service.get_subscriptions()

        sub_service._port.get_bucket_keys.assert_called_once_with(Bucket.credentials)
        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        assert result == [subscription]

    async def test_get_subscriptions_empty_result(self, sub_service: SubscriptionService):
        sub_service._port.get_bucket_keys = AsyncMock(return_value=[])

        result = await sub_service.get_subscriptions()

        sub_service._port.get_bucket_keys.assert_called_once_with(Bucket.credentials)
        assert result == []

    async def test_create_subscription_existing_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service._port.get_str_value = AsyncMock(return_value=CONSUMER_HASHED_PASSWORD)

        result = await sub_service.register_subscription(self.new_subscription)

        assert result is False
        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        sub_service._port.get_str_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.credentials)
        sub_service._port.put_value.assert_not_called()

    @pytest.mark.parametrize(
        "field,value",
        [
            ("request_prefill", False),
            ("password", "wrong_password"),
            ("realms_topics", [(REALM, GROUPS_TOPIC), (REALM, USERS_TOPIC)]),
        ],
    )
    async def test_create_subscription_existing_subscription_different_parameters(
        self, field, value, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service._port.get_str_value = AsyncMock(return_value=CONSUMER_HASHED_PASSWORD)

        new_sub = deepcopy(self.new_subscription)
        setattr(new_sub, field, value)
        with pytest.raises(HTTPException):
            await sub_service.register_subscription(new_sub)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        sub_service._port.put_value.assert_not_called()

    async def test_add_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.get_list_value = AsyncMock(return_value=[])
        sub_service._port.ensure_stream = AsyncMock()
        sub_service._port.ensure_consumer = AsyncMock()

        await sub_service.register_subscription(self.new_subscription)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        sub_service._port.get_list_value.assert_called_once_with("realm:topic.udm:groups/group", Bucket.subscriptions)
        assert sub_service._port.put_value.call_count == 3

    async def test_get_subscription_not_found(self, sub_service):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Subscription was not found."):
            await sub_service.get_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)

    async def test_get_subscription_queue_status_with_no_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Subscription was not found."):
            await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)

    async def test_get_subscription_queue_status_with_subscriptions(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.get_subscription_queue_status(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        assert result == FillQueueStatus.done

    async def test_set_subscription_queue_status_with_no_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Subscription was not found."):
            await sub_service.set_subscription_queue_status(SUBSCRIPTION_NAME, FillQueueStatus.pending)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        sub_service._port.put_value.assert_not_called()

    async def test_set_subscription_queue_status_with_subscriptions(self, sub_service: SubscriptionService):
        sub_info = deepcopy(SUBSCRIPTION_INFO)
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.set_subscription_queue_status(SUBSCRIPTION_NAME, FillQueueStatus.pending)
        sub_info["prefill_queue_status"] = "pending"

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        sub_service._port.put_value.assert_called_once_with(SUBSCRIPTION_NAME, sub_info, Bucket.subscriptions)
        assert result is None

    async def test_delete_subscription_with_no_existing_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError, match="Subscription was not found."):
            await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        sub_service._port.put_value.assert_not_called()

    async def test_delete_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIPTION_NAME])

        await sub_service.delete_subscription(SUBSCRIPTION_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(SUBSCRIPTION_NAME, Bucket.subscriptions)
        sub_service._port.get_list_value.assert_called_once_with(
            "realm:topic." + REALMS_TOPICS_STR, Bucket.subscriptions
        )
        sub_service._port.put_value.assert_called_once_with(
            "realm:topic." + REALMS_TOPICS_STR, [], Bucket.subscriptions
        )
        sub_service._port.delete_kv_pair.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, Bucket.credentials),
                call(SUBSCRIPTION_NAME, Bucket.subscriptions),
            ]
        )
