# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch, call

import aiohttp
import pytest
from nats.aio.msg import Msg

from tests.conftest import SUBSCRIBER_INFO, MESSAGE

from tests.conftest import FakeKvStore, FakeJs, MSG
from dispatcher.port import DispatcherPort
from dispatcher.service.dispatcher import DispatcherService


@pytest.fixture
async def port_with_mock_nats():
    port = DispatcherPort()
    port._nats_adapter.kv_store = FakeKvStore()
    port._nats_adapter.js = FakeJs()
    port._nats_adapter.js.subscribe = AsyncMock()
    port._nats_adapter._future = AsyncMock()
    port._nats_adapter.wait_for_event = AsyncMock(
        side_effect=[MSG, Exception("Stop waiting for the new event")]
    )
    port._nats_adapter.add_message = AsyncMock()
    Msg.in_progress = AsyncMock()
    Msg.ack = AsyncMock()
    async with aiohttp.ClientSession() as session:
        port._consumer_reg_adapter._session = session
    return port


@pytest.mark.anyio
class TestDispatcher:
    @patch("src.shared.adapters.consumer_reg_adapter.aiohttp.ClientSession.get")
    async def test_dispatch_events(
        self,
        mock_get,
        port_with_mock_nats: DispatcherPort,
    ):
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=[SUBSCRIBER_INFO]
        )

        # trigger dispatcher to retrieve event from incoming queue
        service = DispatcherService(port_with_mock_nats)
        try:
            await service.dispatch_events()
        except Exception:
            pass

        # check subscribing to the incoming queue
        port_with_mock_nats._nats_adapter.js.subscribe.assert_called_once_with(
            "incoming",
            cb=port_with_mock_nats._nats_adapter.cb,
            durable="dispatcher-service",
            manual_ack=True,
        )
        # check waiting for the event
        port_with_mock_nats._nats_adapter.wait_for_event.assert_has_calls(
            [call(), call()]
        )
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions?realm_topic=udm:users/user"
        )
        # check storing event in the consumer queue
        port_with_mock_nats._nats_adapter.add_message.assert_called_once_with(
            SUBSCRIBER_INFO["name"], MESSAGE
        )
