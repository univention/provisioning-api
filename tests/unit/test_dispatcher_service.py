# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest

from dispatcher.service.dispatcher import DispatcherService
from tests.conftest import SUBSCRIBER_INFO, REALMS_TOPICS_STR, MESSAGE, MQMESSAGE


@pytest.fixture
def dispatcher_service() -> DispatcherService:
    return DispatcherService(AsyncMock())


@pytest.mark.anyio
class TestDispatcherService:
    async def test_dispatch_events(self, dispatcher_service: DispatcherService):
        dispatcher_service._port.get_realm_topic_subscriptions = AsyncMock(
            return_value=[SUBSCRIBER_INFO]
        )
        dispatcher_service._port.wait_for_event = AsyncMock(
            side_effect=[MQMESSAGE, Exception("Stop waiting for the new event")]
        )

        with pytest.raises(Exception) as e:
            await dispatcher_service.dispatch_events()

        dispatcher_service._port.subscribe_to_queue.assert_called_once_with(
            "incoming", "dispatcher-service"
        )
        dispatcher_service._port.wait_for_event.assert_has_calls([call(), call()])
        dispatcher_service._port.get_realm_topic_subscriptions.assert_called_once_with(
            REALMS_TOPICS_STR
        )
        dispatcher_service._port.send_event_to_consumer_queue.assert_called_once_with(
            SUBSCRIBER_INFO["name"], MESSAGE
        )
        dispatcher_service._port.acknowledge_message_in_progress.assert_called_once_with(
            MQMESSAGE
        )
        dispatcher_service._port.acknowledge_message.assert_called_once_with(MQMESSAGE)
        assert "Stop waiting for the new event" == str(e.value)
