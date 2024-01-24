# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from copy import deepcopy
from unittest.mock import AsyncMock, patch, call

import aiohttp
import pytest

from shared.models import FillQueueStatus
from tests.conftest import (
    FLAT_MESSAGE_ENCODED,
    MSG_FOR_ONE_SUB,
    FLAT_MESSAGE_FOR_ONE_SUB_ENCODED,
    FLAT_MESSAGE_FOR_ONE_SUB,
)
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
        dispatcher_mock.mq_adapter._nats.subscribe.assert_called_once_with(
            "incoming", cb=dispatcher_mock.mq_adapter.cb
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter._message_queue.get.assert_has_calls([call(), call()])
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions/?realm_topic=udm:users/user"
        )
        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter._js.add_consumer.assert_called_once()
        dispatcher_mock.mq_adapter._js.publish.assert_called_once_with(
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
        dispatcher_mock.mq_adapter._message_queue.get = AsyncMock(
            side_effect=[MSG_FOR_ONE_SUB, Exception("Stop waiting for the new event")]
        )

        service = DispatcherService(dispatcher_mock)
        try:
            await service.dispatch_events()
        except Exception:
            pass

        # check subscribing to the incoming queue
        dispatcher_mock.mq_adapter._nats.subscribe.assert_called_once_with(
            "incoming", cb=dispatcher_mock.mq_adapter.cb
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter._message_queue.get.assert_has_calls([call(), call()])
        # check getting info for 1 subscriber
        mock_get.assert_called_once_with(
            f"http://localhost:7777/subscriptions/v1/subscriptions/{SUBSCRIBER_NAME}"
        )
        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter._js.add_consumer.assert_called_once()
        dispatcher_mock.mq_adapter._js.publish.assert_called_once_with(
            SUBSCRIBER_INFO["name"],
            FLAT_MESSAGE_FOR_ONE_SUB_ENCODED,
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
        dispatcher_mock.mq_adapter._message_queue.get = AsyncMock(
            side_effect=[msg, Exception("Stop waiting for the new event")]
        )

        service = DispatcherService(dispatcher_mock)
        try:
            await service.dispatch_events()
        except Exception:
            pass

        # check subscribing to the incoming queue
        dispatcher_mock.mq_adapter._nats.subscribe.assert_called_once_with(
            "incoming", cb=dispatcher_mock.mq_adapter.cb
        )
        # check waiting for the event
        dispatcher_mock.mq_adapter._message_queue.get.assert_has_calls([call(), call()])
        # check getting subscribers for the realm_topic
        mock_get.assert_called_once_with(
            "http://localhost:7777/subscriptions/v1/subscriptions/?realm_topic=udm:users/user"
        )

        # check sending event to the incoming queue for the subscriber
        mock_post.assert_called_once_with(
            "http://localhost:7777/events/v1/events", json=FLAT_MESSAGE_FOR_ONE_SUB
        )
