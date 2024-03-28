# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call

import pytest
from nats.aio.msg import Msg
from tests.conftest import (
    SUBSCRIPTION_NAME,
    MSG,
    MockNatsMQAdapter,
    MockNatsKVAdapter,
    SUBSCRIPTIONS,
    FLAT_MESSAGE_ENCODED,
)
from src.server.core.dispatcher.config import DispatcherSettings
from src.server.core.dispatcher.port import DispatcherPort
from src.server.core.dispatcher.service.dispatcher import DispatcherService


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def dispatcher_mock() -> DispatcherPort:
    port = DispatcherPort(
        DispatcherSettings(nats_user="dispatcher", nats_password="dispatcherpass")
    )
    port.mq_adapter = MockNatsMQAdapter()
    port.kv_adapter = MockNatsKVAdapter()
    port.mq_adapter._message_queue.get = AsyncMock(
        side_effect=[MSG, Exception("Stop waiting for the new event")]
    )
    port.watch_for_changes = AsyncMock()
    Msg.in_progress = AsyncMock()
    Msg.ack = AsyncMock()

    return port


@pytest.mark.anyio
class TestDispatcher:
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
        except Exception:
            pass

        # check subscribing to the incoming queue
        dispatcher_mock.mq_adapter._js.subscribe.assert_called_once_with(
            "incoming",
            cb=dispatcher_mock.mq_adapter.cb,
            durable="durable_name:incoming",
            manual_ack=True,
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter._message_queue.get.assert_has_calls([call(), call()])

        # check getting subscriptions for the realm_topic
        dispatcher_mock.watch_for_changes.assert_called_once_with(SUBSCRIPTIONS)

        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter._js.publish.assert_called_once_with(
            SUBSCRIPTION_NAME,
            FLAT_MESSAGE_ENCODED,
            stream=f"stream:{SUBSCRIPTION_NAME}",
        )
