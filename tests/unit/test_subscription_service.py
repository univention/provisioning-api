# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call
import pytest

from shared.models.subscription import Subscriber
from tests.conftest import (
    SUBSCRIPTION_INFO,
    SUBSCRIBER_NAME,
    REALM,
    TOPIC,
    SUBSCRIBER_BUCKET,
    ENCODED_REALM_TOPIC,
    REALMS_TOPICS_STR,
    SUBSCRIPTION_STREAM_NAME,
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
        name=SUBSCRIBER_NAME,
        realm=REALM,
        topic=TOPIC,
        request_prefill=True,
    )

    # subscription = SubscriptionKeys.subscription(SUBSCRIBER_NAME)

    async def test_get_subscribers(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIBER_NAME])
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service._port.subscriber_exists = AsyncMock(return_value=SUBSCRIBER_BUCKET)
        sub_service._port.get_subscription_names = AsyncMock(
            return_value=[ENCODED_REALM_TOPIC]
        )
        subscriber = Subscriber(
            name=SUBSCRIBER_NAME,
            subscriptions=[
                Subscription(
                    realm=REALM,
                    topic=TOPIC,
                    request_prefill=True,
                    prefill_queue_status="pending",
                )
            ],
        )

        result = await sub_service.get_subscribers()

        sub_service._port.get_list_value.assert_called_once_with(
            SubscriptionKeys.subscribers, "main"
        )
        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.subscriber_exists.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.get_subscription_names.assert_called_once_with(
            SUBSCRIBER_NAME
        )
        assert result == [subscriber]

    async def test_get_subscribers_empty_result(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[])

        result = await sub_service.get_subscribers()

        sub_service._port.get_list_value.assert_called_once_with(
            SubscriptionKeys.subscribers, "main"
        )
        sub_service._port.get_dict_value.assert_not_called()
        sub_service._port.subscriber_exists.assert_not_called()
        sub_service._port.get_subscription_names.assert_not_called()
        assert result == []

    async def test_get_subscriber_not_found(self, sub_service):
        sub_service._port.subscriber_exists = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_info(SUBSCRIBER_NAME)

        sub_service._port.subscriber_exists.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.get_subscription_names.assert_not_called()
        sub_service._port.get_dict_value.assert_not_called()
        assert "Subscriber was not found." == str(e.value)

    async def test_create_subscription_and_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.subscriber_exists = AsyncMock(return_value=None)
        sub_service._port.get_str_value = AsyncMock(return_value="")

        result = await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.create_subscriber.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.get_str_value.assert_called_once_with(
            SubscriptionKeys.subscribers, "main"
        )
        sub_service._port.put_value.assert_has_calls(
            [
                call(SubscriptionKeys.subscribers, SUBSCRIBER_NAME, bucket="main"),
                call(ENCODED_REALM_TOPIC, SUBSCRIPTION_INFO, bucket=SUBSCRIBER_NAME),
            ]
        )
        sub_service._port.create_stream.assert_called_once_with(
            SUBSCRIPTION_STREAM_NAME
        )
        sub_service._port.create_consumer.assert_called_once_with(
            SUBSCRIPTION_STREAM_NAME
        )
        assert result is None

    async def test_create_subscription_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)
        sub_service._port.subscriber_exists = AsyncMock(return_value=SUBSCRIBER_BUCKET)

        with pytest.raises(ValueError) as e:
            await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.put_value.assert_not_called()
        sub_service._port.create_subscriber.assert_not_called()
        sub_service._port.get_str_value.assert_not_called()
        sub_service._port.put_value.assert_not_called()
        sub_service._port.create_stream.assert_not_called()
        sub_service._port.create_consumer.assert_not_called()
        assert "The subscription with the given realm_topic already exists" == str(
            e.value
        )

    async def test_get_subscriber_queue_status_with_no_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscription_queue_status(
                SUBSCRIBER_NAME, ENCODED_REALM_TOPIC
            )

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        assert "Subscription was not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.get_subscription_queue_status(
            SUBSCRIBER_NAME, ENCODED_REALM_TOPIC
        )

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        assert result == FillQueueStatus.pending

    async def test_set_subscription_queue_status_with_no_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.set_subscription_queue_status(
                SUBSCRIBER_NAME, REALMS_TOPICS_STR, FillQueueStatus.pending
            )

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.put_value.assert_not_called()
        assert "Subscription was not found." == str(e.value)

    async def test_set_subscription_queue_status(
        self, sub_service: SubscriptionService
    ):
        sub_info = deepcopy(SUBSCRIPTION_INFO)
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.set_subscription_queue_status(
            SUBSCRIBER_NAME, REALMS_TOPICS_STR, FillQueueStatus.pending
        )
        sub_info["prefill_queue_status"] = "pending"

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.put_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, sub_info, bucket=SUBSCRIBER_NAME
        )
        assert result is None

    async def test_cancel_subscription(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIPTION_INFO)

        result = await sub_service.cancel_subscription(
            SUBSCRIBER_NAME, REALMS_TOPICS_STR
        )

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.delete_kv_pair.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.delete_stream.assert_called_once_with(
            SUBSCRIPTION_STREAM_NAME
        )
        sub_service._port.delete_consumer.assert_called_once_with(
            SUBSCRIPTION_STREAM_NAME
        )
        assert result is None

    async def test_cancel_subscription_with_no_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(SUBSCRIBER_NAME, REALMS_TOPICS_STR)

        sub_service._port.get_dict_value.assert_called_once_with(
            ENCODED_REALM_TOPIC, SUBSCRIBER_NAME
        )
        sub_service._port.delete_kv_pair.assert_not_called()
        sub_service._port.delete_stream.assert_not_called()
        sub_service._port.delete_consumer.assert_not_called()
        assert "Subscription was not found." == str(e.value)
