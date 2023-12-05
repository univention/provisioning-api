from copy import deepcopy
from unittest.mock import AsyncMock, patch, call
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
        sub_service._port.get_list_value = AsyncMock(
            return_value=[self.subscriber_name]
        )
        sub_service._port.get_dict_value = AsyncMock(return_value=self.subscriber_info)
        subscriber = Subscriber(
            name=self.subscriber_name,
            realms_topics=["foo:bar"],
            fill_queue=True,
            fill_queue_status="done",
        )

        result = await sub_service.get_subscribers()

        sub_service._port.get_list_value.assert_called_once_with("subscribers")
        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )

        assert result == [subscriber]

    async def test_get_subscribers_empty_result(self, sub_service):
        sub_service._port.get_list_value = AsyncMock(return_value=[])

        result = await sub_service.get_subscribers()

        sub_service._port.get_list_value.assert_called_once_with("subscribers")
        assert result == []

    async def test_get_subscriber_not_found(self, sub_service):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber(self.subscriber_name)

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        assert "Subscriber not found." == str(e.value)

    async def test_create_subscription_existing_subscriber(
        self, sub_service: SubscriptionService
    ):
        new_sub = deepcopy(self.new_subscriber)
        new_sub.realm_topic = ["abc", "def"]
        sub_info = deepcopy(self.subscriber_info)
        sub_service._port.put_value = AsyncMock()
        sub_service._port.get_dict_value = AsyncMock(return_value=sub_info)
        sub_service._port.get_str_value = AsyncMock(return_value=None)

        await sub_service.create_subscription(new_sub)

        sub_info["realms_topics"].append("abc:def")

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.get_str_value.assert_called_once_with("abc:def")
        sub_service._port.put_value.assert_has_calls(
            [
                call(f"subscriber:{self.subscriber_name}", sub_info),
                call("abc:def", self.subscriber_name),
            ]
        )

    async def test_create_subscription_existing_subscription(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.put_value = AsyncMock()
        sub_service._port.get_dict_value = AsyncMock(return_value=self.subscriber_info)

        with pytest.raises(ValueError) as e:
            await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.put_value.assert_not_called()
        assert "Subscription for the given realm_topic already exists" == str(e.value)

    async def test_add_subscriber(self, sub_service: SubscriptionService):
        sub_service._port.put_value = AsyncMock()
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.get_str_value = AsyncMock(side_effect=[None, None])

        await sub_service.create_subscription(self.new_subscriber)

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.get_str_value.assert_has_calls(
            [call("subscribers"), call("foo:bar")]
        )
        sub_service._port.put_value.assert_has_calls(
            [
                call("subscribers", self.subscriber_name),
                call("foo:bar", self.subscriber_name),
            ]
        )

    async def test_get_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)

        with pytest.raises(ValueError) as e:
            await sub_service.get_subscriber_queue_status(self.subscriber_name)

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        assert "Subscriber not found." == str(e.value)

    async def test_get_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=self.subscriber_info)

        result = await sub_service.get_subscriber_queue_status(self.subscriber_name)

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        assert result == FillQueueStatus.done

    async def test_set_subscriber_queue_status_with_no_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.put_value = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_service.set_subscriber_queue_status(
                self.subscriber_name, FillQueueStatus.pending
            )

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.put_value.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_set_subscriber_queue_status_with_subscribers(
        self, sub_service: SubscriptionService
    ):
        sub_info = deepcopy(self.subscriber_info)
        sub_service._port.get_dict_value = AsyncMock(return_value=self.subscriber_info)
        sub_service._port.put_value = AsyncMock()

        result = await sub_service.set_subscriber_queue_status(
            self.subscriber_name, FillQueueStatus.pending
        )
        sub_info["fill_queue_status"] = "pending"

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.put_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}", sub_info
        )
        assert result is None

    async def test_cancel_subscription_with_no_existing_realm_topic(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=self.subscriber_info)
        sub_service._port.put_value = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(self.subscriber_name, "abc:def")

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.put_value.assert_not_called()
        assert "Subscription for the given realm_topic doesn't exist" == str(e.value)

    async def test_cancel_subscription_with_no_existing_subscriber(
        self, sub_service: SubscriptionService
    ):
        sub_service._port.get_dict_value = AsyncMock(return_value=None)
        sub_service._port.put_value = AsyncMock()

        with pytest.raises(ValueError) as e:
            await sub_service.cancel_subscription(self.subscriber_name, "abc:def")

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.put_value.assert_not_called()
        assert "Subscriber not found." == str(e.value)

    async def test_cancel_subscription(self, sub_service: SubscriptionService):
        sub_info = deepcopy(self.subscriber_info)
        res_sub_info = deepcopy(self.subscriber_info)
        res_sub_info["realms_topics"] = []
        sub_service._port.get_dict_value = AsyncMock(return_value=sub_info)
        sub_service._port.get_list_value = AsyncMock(
            return_value=[self.subscriber_name]
        )
        sub_service._port.put_value = AsyncMock()

        await sub_service.cancel_subscription(self.subscriber_name, "foo:bar")

        sub_service._port.get_dict_value.assert_called_once_with(
            f"subscriber:{self.subscriber_name}"
        )
        sub_service._port.get_list_value.assert_called_once_with(self.realm_topic)
        sub_service._port.put_value.assert_has_calls(
            [
                call(self.realm_topic, ""),
                call(f"subscriber:{self.subscriber_name}", res_sub_info),
            ]
        )
