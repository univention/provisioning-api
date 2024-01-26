from datetime import datetime
from unittest.mock import AsyncMock, patch, call

import pytest

from prefill.service.udm_prefill import UDMPreFill
from shared.models import Message
from tests.conftest import (
    SUBSCRIBER_NAME,
    MSG_PREFILL,
    PREFILL_MESSAGE,
    MSG_PREFILL_REDELIVERED,
)


@pytest.fixture
def udm_prefill() -> UDMPreFill:
    return UDMPreFill(AsyncMock())


@pytest.mark.anyio
class TestUDMPreFill:
    mocked_date = datetime(2023, 11, 9, 11, 15, 52, 616061)
    object_type = "users/user"
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
        publisher_name="udm-pre-fill",
        ts=mocked_date,
        realm="udm",
        topic=object_type,
        body={
            "old": None,
            "new": obj,
        },
    )

    @patch("prefill.service.udm_prefill.datetime")
    async def test_handle_requests_to_prefill(self, mock_datetime, udm_prefill):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._port.wait_for_event = AsyncMock(
            side_effect=[MSG_PREFILL, Exception("Stop waiting for the new event")]
        )
        udm_prefill._port.get_object_types = AsyncMock(return_value=[self.udm_modules])
        udm_prefill._port.list_objects = AsyncMock(return_value=[self.url])
        udm_prefill._port.get_object = AsyncMock(return_value=self.obj)
        MSG_PREFILL.in_progress = AsyncMock()
        MSG_PREFILL.ack = AsyncMock()

        with pytest.raises(Exception) as e:
            await udm_prefill.handle_requests_to_prefill()

        udm_prefill._port.subscribe_to_queue.assert_called_once_with(
            "prefill", "prefill-service"
        )
        udm_prefill._port.create_stream.assert_called_once_with("prefill-failures")
        udm_prefill._port.create_consumer.assert_called_once_with("prefill-failures")
        udm_prefill._port.wait_for_event.assert_has_calls([call(), call()])
        udm_prefill._port.get_object_types.assert_called_once_with()
        udm_prefill._port.list_objects.assert_called_once_with(self.object_type)
        udm_prefill._port.get_object.assert_called_once_with(self.url)
        MSG_PREFILL.in_progress.assert_called_once_with()
        MSG_PREFILL.ack.assert_called_once_with()
        udm_prefill._port.create_prefill_message.assert_called_once_with(
            SUBSCRIBER_NAME, self.msg
        )
        udm_prefill._port.add_request_to_prefill_failures.assert_not_called()

        assert "Stop waiting for the new event" == str(e.value)

    @patch("prefill.service.udm_prefill.datetime")
    async def test_handle_requests_to_prefill_moving_to_failures(
        self, mock_datetime, udm_prefill
    ):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._port.wait_for_event = AsyncMock(
            side_effect=[
                MSG_PREFILL_REDELIVERED,
                Exception("Stop waiting for the new event"),
            ]
        )
        MSG_PREFILL_REDELIVERED.in_progress = AsyncMock()
        MSG_PREFILL_REDELIVERED.ack = AsyncMock()

        with pytest.raises(Exception) as e:
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
        MSG_PREFILL_REDELIVERED.in_progress.assert_not_called()
        MSG_PREFILL_REDELIVERED.ack.assert_called_once_with()
        udm_prefill._port.create_prefill_message.assert_not_called()
        udm_prefill._port.add_request_to_prefill_failures.assert_called_once_with(
            "prefill-failures", PREFILL_MESSAGE
        )

        assert "Stop waiting for the new event" == str(e.value)

    @patch("prefill.service.udm_prefill.datetime")
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
