# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest

from dispatcher.service.dispatcher import DispatcherService
from tests.conftest import (
    MSG,
    REALMS_TOPICS_STR,
    MESSAGE,
    SUBSCRIBER_NAME,
)


@pytest.fixture
def dispatcher_service() -> DispatcherService:
    return DispatcherService(AsyncMock())


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
class TestDispatcherService:
    async def test_dispatch_events(self, dispatcher_service: DispatcherService):
        dispatcher_service._port.get_realm_topic_subscribers = AsyncMock(
            return_value=[SUBSCRIBER_NAME]
        )
        dispatcher_service._port.wait_for_event = AsyncMock(
            side_effect=[MSG, Exception("Stop waiting for the new event")]
        )
        MSG.in_progress = AsyncMock()
        MSG.ack = AsyncMock()

        with pytest.raises(Exception) as e:
            await dispatcher_service.dispatch_events()

        dispatcher_service._port.subscribe_to_queue.assert_called_once_with(
            "incoming", "dispatcher-service"
        )
        dispatcher_service._port.wait_for_event.assert_has_calls([call(), call()])
        dispatcher_service._port.get_realm_topic_subscribers.assert_called_once_with(
            REALMS_TOPICS_STR
        )
        dispatcher_service._port.send_message_to_subscriber.assert_called_once_with(
            SUBSCRIBER_NAME, MESSAGE
        )
        assert "Stop waiting for the new event" == str(e.value)
