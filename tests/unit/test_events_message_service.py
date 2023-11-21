from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest

from events.service import EventsService
from shared.models import Event


@pytest.fixture
def port() -> AsyncMock:
    return patch("events.service.events.EventsPort").start().return_value


@pytest.fixture
def message_service(port) -> EventsService:
    message_repo = EventsService(port)
    return message_repo


@pytest.mark.anyio
class TestEventsMessageService:
    data = Event(
        realm="udm",
        topic="topic_name",
        body={
            "foo": "bar",
            "foo1": "bar1",
        },
    )
    publisher_name = "live_event"
    ts = datetime(2023, 11, 3, 12, 34, 56, 789012)

    async def test_add_live_message(self, message_service: EventsService):
        message_service._port.add_live_event = AsyncMock()

        await message_service.publish_event(self.data, self.publisher_name, self.ts)

        message_service._port.add_live_event.assert_called_once_with(
            self.data, self.publisher_name, self.ts
        )
