# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
from unittest.mock import AsyncMock, patch, call
import pytest
from src.server.core.prefill.service.udm_prefill import UDMPreFill
from src.server.core.prefill.service.udm_prefill import match_topic
from src.shared.models import Message, PublisherName
from tests.conftest import (
    SUBSCRIPTION_NAME,
    PREFILL_MESSAGE,
    MQMESSAGE_PREFILL,
    MQMESSAGE_PREFILL_REDELIVERED,
)


@pytest.fixture
def udm_prefill() -> UDMPreFill:
    return UDMPreFill(AsyncMock())


@pytest.mark.anyio
class TestUDMPreFill:
    mocked_date = datetime(2023, 11, 9, 11, 15, 52, 616061)
    object_type = "groups/group"
    url = f"http://udm-rest-api:9979/udm/{object_type}/..."
    udm_modules = {
        "name": object_type,
        "title": "Group",
        "href": f"http://udm-rest-api:9979/udm/{object_type}/",
    }
    obj = {
        "uri": url,
        "dn": "",
        "objectType": object_type,
        "position": "",
        "properties": {},
        "uuid": "",
    }
    msg = Message(
        publisher_name=PublisherName.udm_pre_fill,
        ts=mocked_date,
        realm="udm",
        topic=object_type,
        body={
            "old": None,
            "new": obj,
        },
    )

    @patch("src.server.core.prefill.service.udm_prefill.datetime")
    async def test_handle_requests_to_prefill(self, mock_datetime, udm_prefill):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._port.wait_for_event = AsyncMock(
            side_effect=[MQMESSAGE_PREFILL, Exception("Stop waiting for the new event")]
        )
        udm_prefill._port.get_object_types = AsyncMock(return_value=[self.udm_modules])
        udm_prefill._port.list_objects = AsyncMock(return_value=[self.url])
        udm_prefill._port.get_object = AsyncMock(return_value=self.obj)

        with pytest.raises(Exception, match="Stop waiting for the new event"):
            await udm_prefill.handle_requests_to_prefill()

        udm_prefill._port.subscribe_to_queue.assert_called_once_with(
            "prefill", "prefill-service"
        )
        udm_prefill._port.create_stream.assert_has_calls(
            [call("prefill-failures"), call(f"prefill_{SUBSCRIPTION_NAME}")]
        )
        udm_prefill._port.create_consumer.assert_called_once_with("prefill-failures")
        udm_prefill._port.wait_for_event.assert_has_calls([call(), call()])
        udm_prefill._port.get_object_types.assert_called_once_with()
        udm_prefill._port.list_objects.assert_called_once_with(self.object_type)
        udm_prefill._port.get_object.assert_called_once_with(self.url)
        udm_prefill._port.acknowledge_message.assert_called_once_with(MQMESSAGE_PREFILL)
        udm_prefill._port.create_prefill_message.assert_called_once_with(
            f"prefill_{SUBSCRIPTION_NAME}", self.msg
        )
        udm_prefill._port.add_request_to_prefill_failures.assert_not_called()

    @patch("src.server.core.prefill.service.udm_prefill.datetime")
    async def test_handle_requests_to_prefill_moving_to_failures(
        self, mock_datetime, udm_prefill
    ):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._port.wait_for_event = AsyncMock(
            side_effect=[
                MQMESSAGE_PREFILL_REDELIVERED,
                Exception("Stop waiting for the new event"),
            ]
        )

        with pytest.raises(Exception, match="Stop waiting for the new event"):
            await udm_prefill.handle_requests_to_prefill()

        udm_prefill._port.subscribe_to_queue.assert_called_once_with(
            "prefill", "prefill-service"
        )
        udm_prefill._port.create_stream.assert_called_once_with("prefill-failures")
        udm_prefill._port.create_consumer.assert_called_once_with("prefill-failures")
        udm_prefill._port.wait_for_event.assert_has_calls([call(), call()])
        udm_prefill._port.get_object_types.assert_not_called()
        udm_prefill._port.list_objects.assert_not_called()
        udm_prefill._port.get_object.assert_not_called()
        udm_prefill._port.acknowledge_message_in_progress.assert_not_called()
        udm_prefill._port.acknowledge_message.assert_called_once_with(
            MQMESSAGE_PREFILL_REDELIVERED
        )
        udm_prefill._port.create_prefill_message.assert_not_called()
        udm_prefill._port.add_request_to_prefill_failures.assert_called_once_with(
            "prefill-failures", PREFILL_MESSAGE
        )

    @patch("src.server.core.prefill.service.udm_prefill.datetime")
    async def test_fetch_no_udm_module(self, mock_datetime, udm_prefill):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._topic = "test-topic"
        udm_prefill._port.get_object_types = AsyncMock(return_value=[self.udm_modules])

        result = await udm_prefill.fetch()

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
