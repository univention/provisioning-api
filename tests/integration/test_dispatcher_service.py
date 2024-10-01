# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest
from nats.aio.msg import Msg

from server.core.dispatcher.config import DispatcherSettings
from server.core.dispatcher.port import DispatcherPort
from server.core.dispatcher.service.dispatcher import DispatcherService
from univention.provisioning.models import DISPATCHER_SUBJECT_TEMPLATE

from ..mock_data import FLAT_MESSAGE_ENCODED, MSG, SUBSCRIPTION_NAME, SUBSCRIPTIONS
from ..mocks import MockNatsKVAdapter, MockNatsMQAdapter


@pytest.fixture
async def dispatcher_mock() -> DispatcherPort:
    port = DispatcherPort(DispatcherSettings(nats_user="dispatcher", nats_password="dispatcherpass"))
    port.mq_adapter = MockNatsMQAdapter()
    port.kv_adapter = MockNatsKVAdapter()
    port.mq_adapter._message_queue.get = AsyncMock(side_effect=[MSG, Exception("Stop waiting for the new event")])
    port.watch_for_subscription_changes = AsyncMock()
    Msg.in_progress = AsyncMock()
    Msg.ack = AsyncMock()

    return port


@pytest.mark.anyio
class TestDispatcher:
    main_subject = DISPATCHER_SUBJECT_TEMPLATE.format(subscription=SUBSCRIPTION_NAME)

    async def test_dispatch_events(
        self,
        dispatcher_mock: DispatcherPort,
    ):
        """
        This abstract test focuses on checking the interaction between the Dispatcher Service and the Nats,
        specifically verifying the usage of the NATS and jetstream. If the technology changes, the test will fail
        """

        # trigger dispatcher to retrieve event from incoming queue
        service = DispatcherService(dispatcher_mock)
        service._subscriptions = SUBSCRIPTIONS

        try:
            await service.dispatch_events()
        except Exception as exc:
            print(f"Ignoring exception: {exc!s}")

        # check subscribing to the incoming queue
        dispatcher_mock.mq_adapter._js.subscribe.assert_called_once_with(
            "incoming",
            cb=dispatcher_mock.mq_adapter.cb,
            durable="durable_name:incoming",
            stream="stream:incoming",
            manual_ack=True,
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter._message_queue.get.assert_has_calls([call(), call()])

        # check getting subscriptions for the realm_topic
        dispatcher_mock.watch_for_subscription_changes.assert_called_once_with(service.update_subscriptions_mapping)

        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter._js.publish.assert_called_once_with(
            self.main_subject,
            FLAT_MESSAGE_ENCODED,
            stream=f"stream:{SUBSCRIPTION_NAME}",
        )
