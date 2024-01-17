from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from prefill import UDMPreFill
from shared.models import Message
from tests.conftest import SUBSCRIBER_NAME


@pytest.fixture
def udm_prefill() -> UDMPreFill:
    return UDMPreFill(AsyncMock(), AsyncMock(), SUBSCRIBER_NAME, "groups/group")


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
        publisher_name="udm-pre-fill",
        ts=mocked_date,
        realm="udm",
        topic=object_type,
        body={
            "old": None,
            "new": obj,
        },
    )

    @patch("prefill.udm.datetime")
    async def test_fetch(self, mock_datetime, udm_prefill):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._port.get_object_types = AsyncMock(return_value=[self.udm_modules])
        udm_prefill._port.list_objects = AsyncMock(return_value=[self.url])
        udm_prefill._port.get_object = AsyncMock(return_value=self.obj)

        result = await udm_prefill.fetch()

        assert result is None
        udm_prefill._port.get_object_types.assert_called_once_with()
        udm_prefill._port.list_objects.assert_called_once_with(self.object_type)
        udm_prefill._port.get_object.assert_called_once_with(self.url)
        udm_prefill._service.add_prefill_message.assert_called_once_with(
            SUBSCRIBER_NAME, self.msg
        )

    @patch("prefill.udm.datetime")
    async def test_fetch_no_udm_module(self, mock_datetime, udm_prefill):
        mock_datetime.now.return_value = self.mocked_date
        udm_prefill._topic = "test-topic"
        udm_prefill._port.get_object_types = AsyncMock(return_value=[self.udm_modules])

        result = await udm_prefill.fetch()

        assert result is None
        udm_prefill._port.get_object_types.assert_called_once_with()
        udm_prefill._port.list_objects.assert_not_called()
        udm_prefill._port.get_object.assert_not_called()
        udm_prefill._service.add_prefill_message.assert_not_called()
