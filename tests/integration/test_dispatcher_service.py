# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from unittest.mock import AsyncMock, call

import pytest

from univention.provisioning.backends.mocks import MockNatsKVAdapter, MockNatsMQAdapter
from univention.provisioning.backends.nats_mq import json_decoder
from univention.provisioning.dispatcher.config import DispatcherSettings
from univention.provisioning.dispatcher.port import DispatcherPort
from univention.provisioning.dispatcher.service import DispatcherService
from univention.provisioning.models.constants import DISPATCHER_SUBJECT_TEMPLATE
from univention.provisioning.testing.mock_data import FLAT_MESSAGE_ENCODED, MSG, SUBSCRIPTION_NAME, SUBSCRIPTIONS


@pytest.fixture
async def dispatcher_mock(mock_nats_kv_adapter, mock_nats_mq_adapter) -> DispatcherPort:
    port = DispatcherPort(DispatcherSettings(nats_user="dispatcher", nats_password="dispatcherpass"))
    port.mq = MockNatsMQAdapter()
    port.kv = MockNatsKVAdapter()
    fake_ack = AsyncMock()
    mod_MSG = deepcopy(MSG)
    mod_MSG.data = json_decoder(mod_MSG.data.decode())
    port.mq.get_one_message = AsyncMock(
        side_effect=[(mod_MSG, fake_ack), StopLoopException("Stop waiting for the new event")]
    )

    return port


class StopLoopException(Exception): ...


@pytest.mark.anyio
class TestDispatcher:
    main_subject = DISPATCHER_SUBJECT_TEMPLATE.format(subscription=SUBSCRIPTION_NAME)

    async def test_dispatch_events(self, dispatcher_mock: DispatcherPort):
        """
        This abstract test focuses on checking the interaction between the Dispatcher Service and the Nats,
        specifically verifying the usage of the NATS and jetstream. If the technology changes, the test will fail
        """

        # trigger dispatcher to retrieve event from incoming queue
        service = DispatcherService(dispatcher_mock)
        service._subscriptions = SUBSCRIPTIONS

        with pytest.raises(ExceptionGroup):
            await service.dispatch_events()

        # check subscribing to the incoming queue
        dispatcher_mock.mq._js.subscribe.assert_called_once_with(
            "incoming",
            cb=dispatcher_mock.mq.cb,
            durable="durable_name:incoming",
            stream="stream:incoming",
            manual_ack=True,
        )
        # check waiting for the event
        dispatcher_mock.mq.get_one_message.assert_has_calls([call(timeout=10), call(timeout=10)])

        # check getting subscriptions for the realm_topic
        dispatcher_mock.watch_for_subscription_changes.assert_called_once_with(service.update_subscriptions_mapping)

        # check storing event in the consumer queue
        dispatcher_mock.mq._js.publish.assert_called_once_with(
            self.main_subject,
            FLAT_MESSAGE_ENCODED,
            stream=f"stream:{SUBSCRIPTION_NAME}",
        )
