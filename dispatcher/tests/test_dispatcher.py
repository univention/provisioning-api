# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from types import SimpleNamespace
from unittest.mock import AsyncMock, call

import pytest
from test_helpers.mock_data import MESSAGE, MQMESSAGE, SUBSCRIPTION_INFO, SUBSCRIPTION_NAME, SUBSCRIPTIONS

from univention.provisioning.backends.message_queue import MessageAckManager
from univention.provisioning.backends.nats_mq import IncomingQueue
from univention.provisioning.dispatcher.mq_adapter_nats import NatsMessageQueueAdapter
from univention.provisioning.dispatcher.service import DispatcherService
from univention.provisioning.dispatcher.subscriptions_port import SubscriptionsPort
from univention.provisioning.models.constants import DISPATCHER_SUBJECT_TEMPLATE


class EscapeLoopException(Exception): ...


@pytest.fixture
def dispatcher_service() -> DispatcherService:
    mq_pull = AsyncMock()
    mq_pull.configure_mock(settings=SimpleNamespace(nats_consumer_name="dispatcher_consumer_name"))

    mq_push = AsyncMock(spec_set=NatsMessageQueueAdapter)
    subscriptions = AsyncMock(spec_set=SubscriptionsPort)

    return DispatcherService(
        ack_manager=MessageAckManager(),
        mq_push=mq_push,
        mq_pull=mq_pull,
        subscriptions=subscriptions,
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
        dispatcher_service.mq_pull.get_one_message = AsyncMock(
            side_effect=[(MQMESSAGE, fake_ack), EscapeLoopException("Stop waiting for the new event")]
        )
        # add settings to dispatcher_service.mq_pull
        dispatcher_service.subscriptions_db.get_all_subscriptions = get_all_subscriptions

        with pytest.raises(ExceptionGroup) as exception:
            await dispatcher_service.run()

        assert isinstance(exception.value.exceptions[0], Exception)
        assert str(exception.value.exceptions[0]) == "Stop waiting for the new event"

        dispatcher_service.mq_pull.initialize_subscription.assert_called_once_with(
            IncomingQueue("dispatcher_consumer_name")
        )
        dispatcher_service.subscriptions_db.watch_for_subscription_changes.assert_called_once_with(
            dispatcher_service.update_subscriptions_mapping
        )
        dispatcher_service.mq_pull.get_one_message.assert_has_calls([call(timeout=10), call(timeout=10)])

        dispatcher_service.mq_push.enqueue_message.assert_called_once_with(IncomingQueue(SUBSCRIPTION_NAME), MESSAGE)
        fake_ack.acknowledge_message.assert_called_once_with()
