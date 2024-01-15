from copy import deepcopy
from unittest.mock import AsyncMock, call

import pytest

from dispatcher.service.dispatcher import DispatcherService
from shared.models import FillQueueStatus
from tests.conftest import (
    MSG,
    SUBSCRIBER_INFO,
    REALMS_TOPICS_STR,
    MESSAGE,
    MSG_FOR_ONE_SUB,
    MESSAGE_FOR_ONE_SUB,
)


@pytest.fixture
def dispatcher_service() -> DispatcherService:
    return DispatcherService(AsyncMock())


@pytest.mark.anyio
class TestDispatcherService:
    async def test_dispatch_events_to_all_subscribers(
        self, dispatcher_service: DispatcherService
    ):
        dispatcher_service._port.get_realm_topic_subscribers = AsyncMock(
            return_value=[SUBSCRIBER_INFO]
        )
        dispatcher_service._port.wait_for_event = AsyncMock(
            side_effect=[MSG, Exception("Stop waiting for the new event")]
        )

        try:
            await dispatcher_service.dispatch_events()
        except Exception:
            pass

        dispatcher_service._port.subscribe_to_queue.assert_called_once_with("incoming")
        dispatcher_service._port.wait_for_event.assert_has_calls([call(), call()])
        dispatcher_service._port.get_realm_topic_subscribers.assert_called_once_with(
            REALMS_TOPICS_STR
        )
        dispatcher_service._port.get_subscriber.assert_not_called()
        dispatcher_service._port.send_event_to_consumer_queue.assert_called_once_with(
            SUBSCRIBER_INFO["name"], MESSAGE
        )
        dispatcher_service._port.send_event_to_incoming_queue.assert_not_called()

    async def test_dispatch_events_to_one_subscriber(
        self, dispatcher_service: DispatcherService
    ):
        dispatcher_service._port.get_subscriber = AsyncMock(
            return_value=SUBSCRIBER_INFO
        )
        dispatcher_service._port.wait_for_event = AsyncMock(
            side_effect=[MSG_FOR_ONE_SUB, Exception("Stop waiting for the new event")]
        )

        try:
            await dispatcher_service.dispatch_events()
        except Exception:
            pass

        dispatcher_service._port.subscribe_to_queue.assert_called_once_with("incoming")
        dispatcher_service._port.wait_for_event.assert_has_calls([call(), call()])
        dispatcher_service._port.get_realm_topic_subscribers.assert_not_called()
        dispatcher_service._port.get_subscriber.assert_called_once_with(
            SUBSCRIBER_INFO["name"]
        )
        dispatcher_service._port.send_event_to_consumer_queue.assert_called_once_with(
            SUBSCRIBER_INFO["name"], MESSAGE_FOR_ONE_SUB
        )
        dispatcher_service._port.send_event_to_incoming_queue.assert_not_called()

    async def test_dispatch_events_to_incoming_queue(
        self, dispatcher_service: DispatcherService
    ):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_info["fill_queue_status"] = FillQueueStatus.pending
        msg = deepcopy(MSG)

        dispatcher_service._port.get_realm_topic_subscribers = AsyncMock(
            return_value=[sub_info]
        )
        dispatcher_service._port.wait_for_event = AsyncMock(
            side_effect=[msg, Exception("Stop waiting for the new event")]
        )

        try:
            await dispatcher_service.dispatch_events()
        except Exception:
            pass

        dispatcher_service._port.subscribe_to_queue.assert_called_once_with("incoming")
        dispatcher_service._port.wait_for_event.assert_has_calls([call(), call()])
        dispatcher_service._port.get_realm_topic_subscribers.assert_called_once_with(
            REALMS_TOPICS_STR
        )
        dispatcher_service._port.get_subscriber.assert_not_called()
        dispatcher_service._port.send_event_to_consumer_queue.assert_not_called
        dispatcher_service._port.send_event_to_incoming_queue.assert_called_once_with(
            MESSAGE_FOR_ONE_SUB
        )
