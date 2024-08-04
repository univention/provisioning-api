# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from copy import deepcopy
from datetime import datetime
from unittest.mock import ANY, AsyncMock, call, patch

import pytest
from server.core.prefill.service.udm_prefill import UDMPreFill, match_topic
from univention.provisioning.models import (
    PREFILL_SUBJECT_TEMPLATE,
    Message,
    PublisherName,
)
from univention.provisioning.models.queue import Body

from tests.conftest import (
    MQMESSAGE_PREFILL,
    MQMESSAGE_PREFILL_MULTIPLE_TOPICS,
    MQMESSAGE_PREFILL_REDELIVERED,
    SUBSCRIPTION_NAME,
    TOPIC,
    TOPIC_2,
)
from tests.unit import EscapeLoopException


@pytest.fixture
def udm_prefill() -> UDMPreFill:
    udm_prefill = UDMPreFill(AsyncMock())
    udm_prefill.max_prefill_attempts = 5
    return udm_prefill


@pytest.mark.anyio
class TestUDMPreFill:
    prefill_subject = PREFILL_SUBJECT_TEMPLATE.format(subscription=SUBSCRIPTION_NAME)
    mocked_date = datetime(2023, 11, 9, 11, 15, 52, 616061)
    url = f"http://udm-rest-api:9979/udm/{TOPIC}/..."
    url_2 = f"http://udm-rest-api:9979/udm/{TOPIC_2}/..."
    udm_modules = {
        "name": TOPIC,
        "title": "Group",
        "href": f"http://udm-rest-api:9979/udm/{TOPIC}/",
    }
    udm_modules_2 = deepcopy(udm_modules)
    udm_modules_2["name"] = TOPIC_2
    udm_modules_2["href"] = f"http://udm-rest-api:9979/udm/{TOPIC_2}/"
    obj = {
        "uri": url,
        "dn": "",
        "objectType": TOPIC,
        "position": "",
        "properties": {},
        "uuid": "",
    }
    obj_2 = deepcopy(obj)
    obj_2["objectType"] = TOPIC_2
    obj_2["uri"] = url_2
    msg = Message(
        publisher_name=PublisherName.udm_pre_fill,
        ts=mocked_date,
        realm="udm",
        topic=TOPIC,
        body=Body(old={}, new=obj),
    )
    msg2 = deepcopy(msg)
    msg2.topic = TOPIC_2
    msg2.body.new = obj_2

    @patch("server.core.prefill.service.udm_prefill.datetime")
    async def test_handle_requests_to_prefill(self, mock_datetime, udm_prefill: UDMPreFill):
        mock_datetime.now.return_value = self.mocked_date
        mock_acknowledgements = AsyncMock()
        udm_prefill._port.get_one_message = AsyncMock(
            side_effect=[
                (MQMESSAGE_PREFILL, mock_acknowledgements),
                EscapeLoopException("Stop waiting for the new event"),
            ]
        )
        udm_prefill._port.get_object_types = AsyncMock(return_value=[self.udm_modules])
        udm_prefill._port.list_objects = AsyncMock(return_value=[self.url])
        udm_prefill._port.get_object = AsyncMock(return_value=self.obj)

        with pytest.raises(EscapeLoopException):
            await udm_prefill.handle_requests_to_prefill()

        udm_prefill._port.initialize_subscription.assert_called_once_with("prefill", None)
        udm_prefill._port.remove_old_messages_from_prefill_subject.assert_called_once_with(
            SUBSCRIPTION_NAME, self.prefill_subject
        )
        udm_prefill._port.get_one_message.assert_has_calls([call(), call()])
        udm_prefill._port.get_object_types.assert_called_once_with()
        udm_prefill._port.list_objects.assert_called_once_with(TOPIC)
        udm_prefill._port.get_object.assert_called_once_with(self.url)
        mock_acknowledgements.acknowledge_message.assert_called_once()
        udm_prefill._port.create_prefill_message.assert_called_once_with(
            SUBSCRIPTION_NAME, self.prefill_subject, self.msg
        )
        udm_prefill._port.add_request_to_prefill_failures.assert_not_called()

    @patch("server.core.prefill.service.udm_prefill.datetime")
    async def test_handle_requests_to_prefill_multiple_topics(self, mock_datetime, udm_prefill: UDMPreFill):
        mock_datetime.now.return_value = self.mocked_date
        mock_acknowledgements = AsyncMock()
        udm_prefill._port.get_one_message = AsyncMock(
            side_effect=[
                (MQMESSAGE_PREFILL_MULTIPLE_TOPICS, mock_acknowledgements),
                EscapeLoopException("Stop waiting for the new event"),
            ]
        )
        udm_prefill._port.get_object_types = AsyncMock(side_effect=[[self.udm_modules], [self.udm_modules_2]])
        udm_prefill._port.list_objects = AsyncMock(side_effect=[[self.url], [self.url_2]])
        udm_prefill._port.get_object = AsyncMock(side_effect=[self.obj, self.obj_2])

        with pytest.raises(EscapeLoopException, match="Stop waiting for the new event"):
            await udm_prefill.handle_requests_to_prefill()

        udm_prefill._port.initialize_subscription.assert_called_once_with("prefill", None)
        udm_prefill._port.remove_old_messages_from_prefill_subject.assert_called_once_with(
            SUBSCRIPTION_NAME, self.prefill_subject
        )
        udm_prefill._port.get_one_message.assert_has_calls([call(), call()])
        udm_prefill._port.get_object_types.assert_has_calls([call(), call()])
        udm_prefill._port.list_objects.assert_has_calls([call(TOPIC), call(TOPIC_2)])
        udm_prefill._port.get_object.assert_has_calls([call(self.url), call(self.url_2)])
        mock_acknowledgements.acknowledge_message.assert_called_once()
        udm_prefill._port.create_prefill_message.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, self.prefill_subject, self.msg),
                call(SUBSCRIPTION_NAME, self.prefill_subject, self.msg2),
            ]
        )
        udm_prefill._port.add_request_to_prefill_failures.assert_not_called()

    @patch("server.core.prefill.service.udm_prefill.datetime")
    async def test_handle_requests_to_prefill_moving_to_failures(self, mock_datetime, udm_prefill: UDMPreFill):
        mock_datetime.now.return_value = self.mocked_date
        mock_acknowledgements = AsyncMock()
        udm_prefill._port.get_one_message = AsyncMock(
            side_effect=[
                (MQMESSAGE_PREFILL_REDELIVERED, mock_acknowledgements),
                EscapeLoopException("Stop waiting for the new event"),
            ]
        )

        with pytest.raises(EscapeLoopException, match="Stop waiting for the new event"):
            await udm_prefill.handle_requests_to_prefill()

        udm_prefill._port.initialize_subscription.assert_called_once_with("prefill", None)
        udm_prefill._port.get_one_message.assert_has_calls([call(), call()])
        udm_prefill._port.get_object_types.assert_not_called()
        udm_prefill._port.list_objects.assert_not_called()
        udm_prefill._port.get_object.assert_not_called()
        udm_prefill._port.acknowledge_message_in_progress.assert_not_called()
        mock_acknowledgements.acknowledge_message.assert_called_once()
        udm_prefill._port.create_prefill_message.assert_not_called()
        udm_prefill._port.add_request_to_prefill_failures.assert_called_once_with(
            "prefill-failures", "prefill-failures", ANY
        )

    @patch("server.core.prefill.service.udm_prefill.datetime")
    async def test_fetch_no_udm_module(self, mock_datetime, udm_prefill: UDMPreFill):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._port.get_object_types = AsyncMock(return_value=[self.udm_modules])

        result = await udm_prefill.fetch_udm("test-subject", "test-topic")

        assert result is None
        udm_prefill._port.get_object_types.assert_called_once_with()
        udm_prefill._port.list_objects.assert_not_called()
        udm_prefill._port.get_object.assert_not_called()
        udm_prefill._port.create_prefill_message.assert_not_called()


class TestMatchMethod:
    def test_subscription_match(self):
        test_cases = [
            # list of test cases:
            # subscription sub.topic, target.topic, expected result
            ("users/user", "users/user", True),
            ("users/user", "groups/group", False),
            ("users/.*", "users/user", True),
            ("users/.*", "groups/group", False),
            (".*", "users/user", True),
            (".*", "groups/group", True),
        ]

        for sub_topic, target_topic, expectation in test_cases:
            assert match_topic(sub_topic, target_topic) == expectation
