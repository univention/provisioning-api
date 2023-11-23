from copy import copy, deepcopy
from unittest.mock import AsyncMock, patch
import pytest

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
    subscriber_name = "subscriber_1"
    realm_topic = "foo:bar"
    subscriber_info = {
        "name": subscriber_name,
        "realms_topics": [realm_topic],
        "fill_queue": True,
        "fill_queue_status": "done",
    }
    new_subscriber = NewSubscriber(
        name=subscriber_name,
        realm_topic=["foo", "bar"],
        fill_queue=True,
    )

    async def test_get_subscribers(self, sub_service):
        sub_service._port.get_subscriber_names = AsyncMock(
            return_value=["subscriber_1"]
        )
        sub_service._port.get_subscriber_info = AsyncMock(
            return_value=self.subscriber_info
        )
        subscriber = Subscriber(
            name=self.subscriber_name,
            realms_topics=["foo:bar"],
            fill_queue=True,
            fill_queue_status="done",
        )

        result = await sub_service.get_subscribers()

        sub_service._port.get_subscriber_names.assert_called_once_with()
        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
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
        sub_service._port.get_subscriber_info = AsyncMock(
            return_value=self.subscriber_info
        )
        sub_service._port.add_subscriber = AsyncMock()
        sub_service._port.create_subscription = AsyncMock()

        await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
        sub_service._port.create_subscription.assert_called_once_with(
            self.subscriber_name, self.realm_topic, self.subscriber_info
        )
        sub_service._port.add_subscriber.assert_not_called()

    async def test_add_subscriber(self, sub_service: SubscriptionService):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=None)
        sub_service._port.add_subscriber = AsyncMock()
        sub_service._port.create_subscription = AsyncMock()

        result = await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
        sub_service._port.add_subscriber.assert_called_once_with(
            self.subscriber_name, self.realm_topic, True, FillQueueStatus.pending
        )
        sub_service._port.create_subscription.assert_not_called()
        assert result is None

    async def test_get_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_queue_status(self.subscriber_name)

        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(
            return_value=self.subscriber_info
        )

        result = await sub_service.get_subscriber_queue_status(self.subscriber_name)

        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
        assert result == FillQueueStatus.done

    async def test_set_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_subscriber_info = AsyncMock(return_value=None)
        sub_service._port.set_subscriber_queue_status = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_queue_status(self.subscriber_name)

        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
        sub_service._port.set_subscriber_queue_status.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_set_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_info = copy(self.subscriber_info)
        sub_service._port.get_subscriber_info = AsyncMock(return_value=sub_info)
        sub_service._port.set_subscriber_queue_status = AsyncMock()

        result = await sub_service.set_subscriber_queue_status(
            self.subscriber_name, FillQueueStatus.pending
        )
        sub_info["fill_queue_status"] = "pending"

        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
        sub_service._port.set_subscriber_queue_status.assert_called_once_with(
            self.subscriber_name, sub_info
        )
        assert result is None

    # FIXME: add needed functionality
    # async def test_cancel_subscription_with_no_existing_realm_topic(self, sub_service: SubscriptionService):
    #     sub_service._port.get_subscriber_info = AsyncMock(return_value=None)
    #     sub_service._port.delete_subscriber = AsyncMock()
    #     sub_service._port.delete_queue = AsyncMock()
    #
    #     with pytest.raises(ValueError) as e:
    #         await sub_service.delete_subscriber(self.subscriber_name)
    #
    #     sub_service._port.get_subscriber_info.assert_called_once_with(
    #         self.subscriber_name
    #     )
    #     sub_service._port.delete_subscriber.assert_not_called()
    #     sub_service._port.delete_queue.assert_not_called()
    #     assert "Subscriber not found." == str(e.value)

    async def test_cancel_subscription(self, sub_service: SubscriptionService):
        sub_info = deepcopy(self.subscriber_info)
        sub_service._port.get_subscriber_info = AsyncMock(return_value=sub_info)
        sub_service._port.update_sub_info = AsyncMock()
        sub_service._port.delete_subscriber = AsyncMock()
        sub_service._port.delete_queue = AsyncMock()

        result = await sub_service.cancel_subscription(
            self.subscriber_name, ["foo", "bar"]
        )

        sub_service._port.get_subscriber_info.assert_called_once_with(
            self.subscriber_name
        )
        sub_service._port.update_sub_info.assert_called_once_with(
            self.subscriber_name, sub_info
        )
        sub_service._port.delete_subscriber.assert_called_once_with(
            self.subscriber_name
        )
        sub_service._port.delete_queue.assert_called_once_with(self.subscriber_name)
        assert result is None
