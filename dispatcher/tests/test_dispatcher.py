# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest
from test_helpers.mock_data import MESSAGE, MQMESSAGE, SUBSCRIPTION_INFO, SUBSCRIPTIONS

from univention.provisioning.backends.message_queue import MessageAckManager
from univention.provisioning.dispatcher.mq_port import MessageQueuePort
from univention.provisioning.dispatcher.service import DispatcherService
from univention.provisioning.dispatcher.subscriptions_port import SubscriptionsPort
from univention.provisioning.models.constants import DISPATCHER_SUBJECT_TEMPLATE


class EscapeLoopException(Exception): ...


@pytest.fixture
def dispatcher_service() -> DispatcherService:
    return DispatcherService(
        ack_manager=MessageAckManager(),
        mq=AsyncMock(spec_set=MessageQueuePort),
        subscriptions=AsyncMock(spec_set=SubscriptionsPort),
    )


async def get_all_subscriptions():
    for i in SUBSCRIPTIONS.values():
        for j in i.values():
            for sub in j:
                yield sub


@pytest.mark.anyio
class TestDispatcherService:
    main_subject = DISPATCHER_SUBJECT_TEMPLATE.format(subscription=SUBSCRIPTION_INFO["name"])

    async def test_dispatch_events(self, dispatcher_service: DispatcherService):
        fake_ack = AsyncMock()
        dispatcher_service.mq.get_one_message = AsyncMock(
            side_effect=[(MQMESSAGE, fake_ack), EscapeLoopException("Stop waiting for the new event")]
        )
        dispatcher_service.subscriptions_db.get_all_subscriptions = get_all_subscriptions

        with pytest.raises(ExceptionGroup) as exception:
            await dispatcher_service.run()

        assert isinstance(exception.value.exceptions[0], Exception)
        assert str(exception.value.exceptions[0]) == "Stop waiting for the new event"

        dispatcher_service.mq.initialize_subscription.assert_called_once_with("incoming", False, "incoming")
        dispatcher_service.subscriptions_db.watch_for_subscription_changes.assert_called_once_with(
            dispatcher_service.update_subscriptions_mapping
        )
        dispatcher_service.mq.get_one_message.assert_has_calls([call(timeout=10), call(timeout=10)])
        dispatcher_service.mq.enqueue_message.assert_called_once_with(SUBSCRIPTION_INFO["name"], MESSAGE)
        fake_ack.acknowledge_message.assert_called_once_with()
