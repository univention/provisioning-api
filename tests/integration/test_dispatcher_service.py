# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, patch, call

import aiohttp
import httpx
import pytest

from shared.models import FillQueueStatus
from tests.conftest import (
    SUBSCRIBER_INFO,
    MSG_FOR_ONE_SUB,
    MESSAGE,
    MESSAGE_FOR_ONE_SUB,
    FLAT_MESSAGE_FOR_ONE_SUB,
    SUBSCRIBER_NAME,
)
from consumer.main import app as messages_app

from tests.conftest import FakeKvStore, FakeJs, MSG
from dispatcher.port import DispatcherPort
from dispatcher.service.dispatcher import DispatcherService
from consumer.main import app


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def producer():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
async def consumer():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def port_with_mock_nats():
    port = DispatcherPort()
    port._nats_adapter.kv_store = FakeKvStore()
    port._nats_adapter.js = FakeJs()
    port._nats_adapter.nats = AsyncMock()
    port._nats_adapter._future = AsyncMock()
    port._nats_adapter.wait_for_event = AsyncMock(
        side_effect=[MSG, Exception("Stop waiting for the new event")]
    )
    port._nats_adapter.add_message = AsyncMock()
    async with aiohttp.ClientSession() as session:
        port._consumer_reg_adapter._session = session
        port._event_adapter._session = session
    return port


@pytest.fixture(scope="session")
async def messages_client():
    async with httpx.AsyncClient(
        app=messages_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.anyio
class TestDispatcher:
    @patch("src.shared.adapters.consumer_reg_adapter.aiohttp.ClientSession.get")
    async def test_dispatch_events_to_all_subscribers(
        self,
        mock_get,
        producer: httpx.AsyncClient,
        consumer: httpx.AsyncClient,
        messages_client: httpx.AsyncClient,
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
        port_with_mock_nats._nats_adapter.nats.subscribe.assert_called_once_with(
            "incoming", cb=port_with_mock_nats._nats_adapter.cb
        )
        # check waiting for the event
        port_with_mock_nats._nats_adapter.wait_for_event.assert_has_calls(
            [call(), call()]
        )
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions/?realm_topic=udm:users/user"
        )
        # check storing event in the consumer queue
        port_with_mock_nats._nats_adapter.add_message.assert_called_once_with(
            SUBSCRIBER_INFO["name"], MESSAGE
        )

    @patch("src.shared.adapters.consumer_reg_adapter.aiohttp.ClientSession.get")
    async def test_dispatch_events_to_one_subscriber(
        self,
        mock_get,
        producer: httpx.AsyncClient,
        consumer: httpx.AsyncClient,
        messages_client: httpx.AsyncClient,
        port_with_mock_nats: DispatcherPort,
    ):
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=SUBSCRIBER_INFO
        )

        # trigger dispatcher to retrieve event from incoming queue
        port_with_mock_nats._nats_adapter.wait_for_event = AsyncMock(
            side_effect=[MSG_FOR_ONE_SUB, Exception("Stop waiting for the new event")]
        )

        service = DispatcherService(port_with_mock_nats)
        try:
            await service.dispatch_events()
        except Exception:
            pass

        # check subscribing to the incoming queue
        port_with_mock_nats._nats_adapter.nats.subscribe.assert_called_once_with(
            "incoming", cb=port_with_mock_nats._nats_adapter.cb
        )
        # check waiting for the event
        port_with_mock_nats._nats_adapter.wait_for_event.assert_has_calls(
            [call(), call()]
        )
        # check getting info for 1 subscriber
        mock_get.assert_called_once_with(
            f"http://localhost:7777/subscriptions/v1/subscriptions/{SUBSCRIBER_NAME}"
        )
        # check storing event in the consumer queue
        port_with_mock_nats._nats_adapter.add_message.assert_called_once_with(
            SUBSCRIBER_NAME, MESSAGE_FOR_ONE_SUB
        )

    @patch("src.shared.adapters.event_adapter.aiohttp.ClientSession.post")
    @patch("src.shared.adapters.consumer_reg_adapter.aiohttp.ClientSession.get")
    async def test_dispatch_events_to_incoming_queue(
        self,
        mock_get,
        mock_post,
        producer: httpx.AsyncClient,
        consumer: httpx.AsyncClient,
        messages_client: httpx.AsyncClient,
        port_with_mock_nats: DispatcherPort,
    ):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_info["fill_queue_status"] = FillQueueStatus.pending
        msg = deepcopy(MSG)
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=[sub_info]
        )

        # trigger dispatcher to retrieve event from incoming queue
        port_with_mock_nats._nats_adapter.wait_for_event = AsyncMock(
            side_effect=[msg, Exception("Stop waiting for the new event")]
        )

        service = DispatcherService(port_with_mock_nats)
        try:
            await service.dispatch_events()
        except Exception:
            pass

        # check subscribing to the incoming queue
        port_with_mock_nats._nats_adapter.nats.subscribe.assert_called_once_with(
            "incoming", cb=port_with_mock_nats._nats_adapter.cb
        )
        # check waiting for the event
        port_with_mock_nats._nats_adapter.wait_for_event.assert_has_calls(
            [call(), call()]
        )
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions/?realm_topic=udm:users/user"
        )

        # check sending event to the incoming queue for the subscriber
        mock_post.assert_called_once_with(
            "http://localhost:7777/events/v1/events", json=FLAT_MESSAGE_FOR_ONE_SUB
        )
