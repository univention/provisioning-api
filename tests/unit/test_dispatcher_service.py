# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest

from server.core.dispatcher.service.dispatcher import DispatcherService
from univention.provisioning.models import DISPATCHER_SUBJECT_TEMPLATE

from tests.conftest import (
    MESSAGE,
    MQMESSAGE,
    SUBSCRIPTION_INFO,
    SUBSCRIPTIONS,
)
from tests.unit import EscapeLoopException


@pytest.fixture
def dispatcher_service() -> DispatcherService:
    return DispatcherService(AsyncMock())


@pytest.mark.anyio
class TestDispatcherService:
    main_subject = DISPATCHER_SUBJECT_TEMPLATE.format(subscription=SUBSCRIPTION_INFO["name"])

    async def test_dispatch_events(self, dispatcher_service: DispatcherService):
        dispatcher_service._subscriptions = SUBSCRIPTIONS
        dispatcher_service._port.wait_for_event = AsyncMock(
            side_effect=[MQMESSAGE, EscapeLoopException("Stop waiting for the new event")]
        )

        with pytest.raises(ExceptionGroup) as exception:
            await dispatcher_service.dispatch_events()

        assert isinstance(exception.value.exceptions[0], Exception)
        assert str(exception.value.exceptions[0]) == "Stop waiting for the new event"

        dispatcher_service._port.subscribe_to_queue.assert_called_once_with("incoming", "dispatcher-service")
        dispatcher_service._port.watch_for_changes.assert_called_once_with(SUBSCRIPTIONS)
        dispatcher_service._port.wait_for_event.assert_has_calls([call(), call()])
        dispatcher_service._port.send_message_to_subscription.assert_called_once_with(
            SUBSCRIPTION_INFO["name"], self.main_subject, MESSAGE
        )
        dispatcher_service._port.acknowledge_message.assert_called_once_with(MQMESSAGE)
