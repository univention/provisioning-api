# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, patch, call

import aiohttp
import pytest
from tests.conftest import FLAT_MESSAGE_ENCODED, FLAT_MES_FOR_ONE_SUB_ENCODED
from tests.conftest import set_up_fake_js, set_up_fake_kv_store

from shared.models import FillQueueStatus
from tests.conftest import (
    SUBSCRIBER_INFO,
    MSG_FOR_ONE_SUB,
    FLAT_MESSAGE_FOR_ONE_SUB,
    SUBSCRIBER_NAME,
)

from tests.conftest import MSG
from dispatcher.port import DispatcherPort
from dispatcher.service.dispatcher import DispatcherService


@pytest.fixture
async def dispatcher_mock() -> DispatcherPort:
    port = DispatcherPort()
    set_up_fake_js(port.mq_adapter)
    set_up_fake_js(port.kv_adapter)
    set_up_fake_kv_store(port.kv_adapter)
    port.mq_adapter.message_queue.get = AsyncMock(
        side_effect=[MSG, Exception("Stop waiting for the new event")]
    )
    port.mq_adapter.nats = AsyncMock()
    async with aiohttp.ClientSession() as session:
        port._consumer_reg_adapter._session = session
        port._event_adapter._session = session
    return port


@pytest.mark.anyio
class TestDispatcher:
    @patch("src.shared.adapters.consumer_reg_adapter.aiohttp.ClientSession.get")
    async def test_store_event_in_the_consumer_queue(
        self, mock_get, dispatcher_mock: DispatcherPort
    ):
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
        dispatcher_mock.mq_adapter.nats.subscribe.assert_called_once_with(
            "incoming", cb=dispatcher_mock.mq_adapter.cb
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter.message_queue.get.assert_has_calls([call(), call()])
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions/?realm_topic=udm:users/user"
        )
        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter.js.add_consumer.assert_called_once()
        dispatcher_mock.mq_adapter.js.publish.assert_called_once_with(
            SUBSCRIBER_INFO["name"],
            FLAT_MESSAGE_ENCODED,
            stream=f"stream:{SUBSCRIBER_NAME}",
        )

    @patch("src.shared.adapters.consumer_reg_adapter.aiohttp.ClientSession.get")
    async def test_dispatch_events_to_one_subscriber(
        self,
        mock_get,
        dispatcher_mock: DispatcherPort,
    ):
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=SUBSCRIBER_INFO
        )

        # trigger dispatcher to retrieve event from incoming queue
        dispatcher_mock.mq_adapter.message_queue.get = AsyncMock(
            side_effect=[MSG_FOR_ONE_SUB, Exception("Stop waiting for the new event")]
        )

        service = DispatcherService(dispatcher_mock)
        try:
            await service.dispatch_events()
        except Exception:
            pass

        # check subscribing to the incoming queue
        dispatcher_mock.mq_adapter.nats.subscribe.assert_called_once_with(
            "incoming", cb=dispatcher_mock.mq_adapter.cb
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter.message_queue.get.assert_has_calls([call(), call()])
        # check getting info for 1 subscriber
        mock_get.assert_called_once_with(
            f"http://localhost:7777/subscriptions/v1/subscriptions/{SUBSCRIBER_NAME}"
        )
        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter.js.add_consumer.assert_called_once()
        dispatcher_mock.mq_adapter.js.publish.assert_called_once_with(
            SUBSCRIBER_INFO["name"],
            FLAT_MES_FOR_ONE_SUB_ENCODED,
            stream=f"stream:{SUBSCRIBER_NAME}",
        )

    @patch("src.shared.adapters.event_adapter.aiohttp.ClientSession.post")
    @patch("src.shared.adapters.consumer_reg_adapter.aiohttp.ClientSession.get")
    async def test_dispatch_events_to_incoming_queue(
        self,
        mock_get,
        mock_post,
        dispatcher_mock: DispatcherPort,
    ):
        sub_info = deepcopy(SUBSCRIBER_INFO)
        sub_info["fill_queue_status"] = FillQueueStatus.pending
        msg = deepcopy(MSG)
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=[sub_info]
        )

        # trigger dispatcher to retrieve event from incoming queue
        dispatcher_mock.mq_adapter.message_queue.get = AsyncMock(
            side_effect=[msg, Exception("Stop waiting for the new event")]
        )

        service = DispatcherService(dispatcher_mock)
        try:
            await service.dispatch_events()
        except Exception:
            pass

        # check subscribing to the incoming queue
        dispatcher_mock.mq_adapter.nats.subscribe.assert_called_once_with(
            "incoming", cb=dispatcher_mock.mq_adapter.cb
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter.message_queue.get.assert_has_calls([call(), call()])
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions/?realm_topic=udm:users/user"
        )

        # check sending event to the incoming queue for the subscriber
        mock_post.assert_called_once_with(
            "http://localhost:7777/events/v1/events", json=FLAT_MESSAGE_FOR_ONE_SUB
        )
