# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call

import pytest

from server.core.dispatcher.config import DispatcherSettings
from server.core.dispatcher.port import DispatcherPort
from server.core.dispatcher.service.dispatcher import DispatcherService
from src.server.adapters.nats_adapter import json_decoder
from univention.provisioning.models import DISPATCHER_SUBJECT_TEMPLATE

from ..mock_data import FLAT_MESSAGE_ENCODED, MSG, SUBSCRIPTION_NAME, SUBSCRIPTIONS
from ..mocks import MockNatsKVAdapter, MockNatsMQAdapter


@pytest.fixture
async def dispatcher_mock() -> DispatcherPort:
    port = DispatcherPort(DispatcherSettings(nats_user="dispatcher", nats_password="dispatcherpass"))
    port.mq_adapter = MockNatsMQAdapter()
    port.kv_adapter = MockNatsKVAdapter()
    fake_ack = AsyncMock()
    mod_MSG = deepcopy(MSG)
    mod_MSG.data = json_decoder(mod_MSG.data.decode())
    port.mq_adapter.get_one_message = AsyncMock(
        side_effect=[(mod_MSG, fake_ack), StopLoopException("Stop waiting for the new event")]
    )
    port.watch_for_subscription_changes = AsyncMock()
    mod_MSG.in_progress = AsyncMock()
    mod_MSG.ack = AsyncMock()

    return port


class StopLoopException(Exception): ...


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

        with pytest.raises(ExceptionGroup):
            await service.dispatch_events()

        # check waiting for the event
        dispatcher_mock.mq_adapter.get_one_message.assert_has_calls([call(timeout=10), call(timeout=10)])

        # check getting subscriptions for the realm_topic
        dispatcher_mock.watch_for_subscription_changes.assert_called_once_with(service.update_subscriptions_mapping)

        # check storing event in the consumer queue
        dispatcher_mock.mq_adapter._js.publish.assert_called_once_with(
            self.main_subject,
            FLAT_MESSAGE_ENCODED,
            stream=f"stream:{SUBSCRIPTION_NAME}",
        )
