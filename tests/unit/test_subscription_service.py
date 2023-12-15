from copy import deepcopy
from unittest.mock import AsyncMock, patch
import pytest

from tests.conftest import (
    SUBSCRIBER_INFO,
    REALM,
    TOPIC,
    REALM_TOPIC,
    SUBSCRIBER_NAME,
    REALMS_TOPICS,
)
from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import Subscriber, NewSubscriber, FillQueueStatus


@pytest.fixture
def port() -> AsyncMock:
    return (
        patch("consumer.subscriptions.service.subscription.ConsumerPort")
        .start()
        .return_value
    )


@pytest.fixture
def sub_service(port) -> SubscriptionService:
    sub_service = SubscriptionService(port)
    return sub_service


@pytest.mark.anyio
class TestSubscriptionService:
    realm_topic = f"{REALM}:{TOPIC}"
    new_subscriber = NewSubscriber(
        name=SUBSCRIBER_NAME,
        realm_topic=REALM_TOPIC,
        fill_queue=True,
    )

    async def test_get_subscribers(self, sub_service):
        sub_service._port.get_subscriber_names = AsyncMock(
            return_value=[SUBSCRIBER_NAME]
        )
        sub_service._port.get_subscriber_info = AsyncMock(return_value=SUBSCRIBER_INFO)
        subscriber = Subscriber(
            name=SUBSCRIBER_NAME,
            realms_topics=REALMS_TOPICS,
            fill_queue=True,
            fill_queue_status="done",
        )

        result = await sub_service.get_subscribers()

        sub_service._port.get_subscriber_names.assert_called_once_with()
        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        assert result == [subscriber]

    async def test_get_subscribers_empty_result(self, sub_service):
        sub_service._port.get_subscriber_names = AsyncMock(return_value=[])
        sub_service._port.get_subscriber_info = AsyncMock()

        result = await sub_service.get_subscribers()

        sub_service._port.get_subscriber_names.assert_called_once_with()
        sub_service._port.get_subscriber_info.assert_not_called()
        assert result == []

    async def test_create_subscription_existing_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_info = deepcopy(self.new_subscriber)
        sub_info.realm_topic = ["abc", "def"]
        sub_service._port.get_subscriber_info = AsyncMock(return_value=SUBSCRIBER_INFO)
        sub_service._port.add_subscriber = AsyncMock()
        sub_service._port.create_subscription = AsyncMock()

        await sub_service.create_subscription(sub_info)

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.create_subscription.assert_called_once_with(
            SUBSCRIBER_NAME, "abc:def", SUBSCRIBER_INFO
        )
        sub_service._port.add_subscriber.assert_not_called()

    async def test_create_subscription_already_exists(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=SUBSCRIBER_INFO)
        sub_service._port.add_subscriber = AsyncMock()
        sub_service._port.create_subscription = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.create_subscription.assert_not_called()
        sub_service._port.add_subscriber.assert_not_called()
        assert "Subscription for the given realm_topic already exists" == str(e.value)

    async def test_add_subscriber(self, sub_service: SubscriptionService):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=None)
        sub_service._port.add_subscriber = AsyncMock()
        sub_service._port.create_subscription = AsyncMock()

        result = await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.add_subscriber.assert_called_once_with(
            SUBSCRIBER_NAME, self.realm_topic, True, FillQueueStatus.pending
        )
        sub_service._port.create_subscription.assert_not_called()
        assert result is None

    async def test_get_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_queue_status(SUBSCRIBER_NAME)

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=SUBSCRIBER_INFO)

        result = await sub_service.get_subscriber_queue_status(SUBSCRIBER_NAME)

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        assert result == FillQueueStatus.done

    async def test_set_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=None)
        sub_service._port.set_subscriber_queue_status = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_queue_status(SUBSCRIBER_NAME)

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.set_subscriber_queue_status.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_set_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_service._port.get_subscriber_info = AsyncMock(return_value=sub_info)
        sub_service._port.set_subscriber_queue_status = AsyncMock()

        result = await sub_service.set_subscriber_queue_status(
            SUBSCRIBER_NAME, FillQueueStatus.pending
        )
        sub_info["fill_queue_status"] = "pending"

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.set_subscriber_queue_status.assert_called_once_with(
            SUBSCRIBER_NAME, sub_info
        )
        assert result is None

    async def test_cancel_subscription_with_no_existing_realm_topic(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=SUBSCRIBER_INFO)
        sub_service._port.delete_subscriber = AsyncMock()
        sub_service._port.delete_queue = AsyncMock()
        sub_service._port.update_sub_info = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(SUBSCRIBER_NAME, "abc:def")

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.delete_subscriber.assert_not_called()
        sub_service._port.delete_queue.assert_not_called()
        sub_service._port.update_sub_info.assert_not_called()
        assert "Subscription for the given realm_topic doesn't exist" == str(e.value)

    async def test_cancel_subscription(self, sub_service: SubscriptionService):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_service._port.get_subscriber_info = AsyncMock(return_value=sub_info)
        sub_service._port.update_sub_info = AsyncMock()
        sub_service._port.delete_subscriber = AsyncMock()
        sub_service._port.delete_queue = AsyncMock()

        result = await sub_service.cancel_subscription(
            SUBSCRIBER_NAME, self.realm_topic
        )

        sub_service._port.get_subscriber_info.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.update_sub_info.assert_called_once_with(
            SUBSCRIBER_NAME, sub_info
        )
        sub_service._port.delete_subscriber.assert_called_once_with(SUBSCRIBER_NAME)
        sub_service._port.delete_queue.assert_called_once_with(SUBSCRIBER_NAME)
        assert result is None
