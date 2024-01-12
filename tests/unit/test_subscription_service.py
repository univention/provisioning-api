# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call
import pytest

from tests.conftest import (
    SUBSCRIBER_INFO,
    REALM_TOPIC,
    SUBSCRIBER_NAME,
    REALMS_TOPICS_STR,
)
from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import Subscriber, NewSubscriber, FillQueueStatus


@pytest.fixture
def sub_service() -> SubscriptionService:
    return SubscriptionService(AsyncMock())


@pytest.mark.anyio
class TestSubscriptionService:
    new_subscriber = NewSubscriber(
        name=SUBSCRIBER_NAME,
        realm_topic=REALM_TOPIC,
        fill_queue=True,
    )
    subscriber = f"subscriber:{SUBSCRIBER_NAME}"

    async def test_get_subscribers(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIBER_NAME])
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)
        subscriber = Subscriber(
            name=SUBSCRIBER_NAME,
            realms_topics=[REALMS_TOPICS_STR],
            fill_queue=True,
            fill_queue_status="done",
        )

        result = await sub_service.get_subscribers(None)

        sub_service._port.get_list_value.assert_called_once_with("subscribers")
        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        assert result == [subscriber]

    async def test_get_subscribers_empty_result(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[])

        result = await sub_service.get_subscribers(None)

        sub_service._port.get_list_value.assert_called_once_with("subscribers")
        assert result == []

    async def test_get_subscriber_not_found(self, sub_service):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber(SUBSCRIBER_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        assert "Subscriber not found." == str(e.value)

    async def test_create_subscription_existing_subscriber(
        self, sub_service: SubscriptionService
    ):
        new_sub = deepcopy(self.new_subscriber)
        new_sub.realm_topic = ["abc", "def"]
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_service._port.get_dict_value = AsyncMock(return_value=sub_info)
        sub_service._port.get_str_value = AsyncMock(return_value=None)

        await sub_service.create_subscription(new_sub)

        sub_info["realms_topics"].append("abc:def")

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.get_str_value.assert_called_once_with("abc:def")
        sub_service._port.put_value.assert_has_calls(
            [
                call(self.subscriber, sub_info),
                call("abc:def", SUBSCRIBER_NAME),
            ]
        )

    async def test_create_subscription_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        with pytest.raises(ValueError) as e:
            await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.put_value.assert_not_called()
        assert "Subscription for the given realm_topic already exists" == str(e.value)

    async def test_add_subscriber(self, sub_service: SubscriptionService):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.get_str_value = AsyncMock(side_effect=[None, None])

        await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.get_str_value.assert_has_calls(
            [call("subscribers"), call("udm:users/user")]
        )
        sub_service._port.put_value.assert_has_calls(
            [
                call("subscribers", SUBSCRIBER_NAME),
                call("udm:users/user", SUBSCRIBER_NAME),
            ]
        )

    async def test_get_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_queue_status(SUBSCRIBER_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        result = await sub_service.get_subscriber_queue_status(SUBSCRIBER_NAME)

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        assert result == FillQueueStatus.done

    async def test_set_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.set_subscriber_queue_status(
                SUBSCRIBER_NAME, FillQueueStatus.pending
            )

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.put_value.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_set_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        result = await sub_service.set_subscriber_queue_status(
            SUBSCRIBER_NAME, FillQueueStatus.pending
        )
        sub_info["fill_queue_status"] = "pending"

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.put_value.assert_called_once_with(self.subscriber, sub_info)
        assert result is None

    async def test_cancel_subscription_with_no_existing_realm_topic(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=SUBSCRIBER_INFO)

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(SUBSCRIBER_NAME, "abc:def")

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.put_value.assert_not_called()
        assert "Subscription for the given realm_topic doesn't exist" == str(e.value)

    async def test_cancel_subscription_with_no_existing_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(SUBSCRIBER_NAME, "abc:def")

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.put_value.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_cancel_subscription(self, sub_service: SubscriptionService):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        res_sub_info = deepcopy(SUBSCRIBER_INFO)
        res_sub_info["realms_topics"] = []
        sub_service._port.get_dict_value = AsyncMock(return_value=sub_info)
        sub_service._port.get_list_value = AsyncMock(return_value=[SUBSCRIBER_NAME])

        await sub_service.cancel_subscription(SUBSCRIBER_NAME, "udm:users/user")

        sub_service._port.get_dict_value.assert_called_once_with(self.subscriber)
        sub_service._port.get_list_value.assert_called_once_with(REALMS_TOPICS_STR)
        sub_service._port.put_list_value.assert_called_once_with(REALMS_TOPICS_STR, [])
        sub_service._port.put_value.assert_called_once_with(
            self.subscriber, res_sub_info
        )
