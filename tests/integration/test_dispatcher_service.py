# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch, call

import aiohttp
import pytest
from nats.aio.msg import Msg

from tests.conftest import FLAT_MESSAGE_ENCODED

from tests.conftest import MockNatsMQAdapter, MockNatsKVAdapter

from tests.conftest import (
    SUBSCRIBER_INFO,
    SUBSCRIBER_NAME,
)

from tests.conftest import MSG
from dispatcher.port import DispatcherPort
from dispatcher.service.dispatcher import DispatcherService


@pytest.fixture
async def dispatcher_mock() -> DispatcherPort:
    port = DispatcherPort()
    port.mq_adapter = MockNatsMQAdapter()
    port.kv_adapter = MockNatsKVAdapter()
    port.mq_adapter._message_queue.get = AsyncMock(
        side_effect=[MSG, Exception("Stop waiting for the new event")]
    )
    Msg.in_progress = AsyncMock()
    Msg.ack = AsyncMock()
    async with aiohttp.ClientSession() as session:
        port._consumer_registration_adapter._session = session
    return port


@pytest.mark.anyio
class TestDispatcher:
    @patch(
        "src.shared.adapters.consumer_registration_adapter.aiohttp.ClientSession.get"
    )
    async def test_dispatch_events(
        self,
        mock_get,
        dispatcher_mock: DispatcherPort,
    ):
        """
        This abstract test focuses on checking the interaction between the Dispatcher Service and the Nats,
        specifically verifying the usage of the NATS and jetstream. If the technology changes, the test will fail
        """
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=[SUBSCRIBER_INFO]
        )

        # trigger dispatcher to retrieve event from incoming queue
        service = DispatcherService(dispatcher_mock)

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
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions?realm_topic=udm:groups/group"
        )
        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter._js.publish.assert_called_once_with(
            SUBSCRIBER_INFO["name"],
            FLAT_MESSAGE_ENCODED,
            stream=f"stream:{SUBSCRIBER_NAME}",
        )
