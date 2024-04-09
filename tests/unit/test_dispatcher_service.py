# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call
import pytest
from server.core.dispatcher.service.dispatcher import DispatcherService
from tests.conftest import (
    SUBSCRIPTION_INFO,
    MESSAGE,
    MQMESSAGE,
    SUBSCRIPTIONS,
)


@pytest.fixture
def dispatcher_service() -> DispatcherService:
    return DispatcherService(AsyncMock())


@pytest.mark.anyio
class TestDispatcherService:
    async def test_dispatch_events(self, dispatcher_service: DispatcherService):
        dispatcher_service._subscriptions = SUBSCRIPTIONS
        dispatcher_service._port.wait_for_event = AsyncMock(
            side_effect=[MQMESSAGE, Exception("Stop waiting for the new event")]
        )

        with pytest.raises(Exception, match="Stop waiting for the new event"):
            await dispatcher_service.dispatch_events()

        dispatcher_service._port.subscribe_to_queue.assert_called_once_with(
            "incoming", "dispatcher-service"
        )
        dispatcher_service._port.watch_for_changes.assert_called_once_with(
            SUBSCRIPTIONS
        )
        dispatcher_service._port.wait_for_event.assert_has_calls([call(), call()])
        dispatcher_service._port.send_message_to_subscription.assert_called_once_with(
            SUBSCRIPTION_INFO["name"], MESSAGE
        )
        dispatcher_service._port.acknowledge_message.assert_called_once_with(MQMESSAGE)
