from datetime import datetime
from unittest.mock import AsyncMock, patch
import pytest

from events.service import MessageService
from shared.models import Message, NewMessage


@pytest.fixture
def port() -> AsyncMock:
    return patch("events.service.messages.EventsPort").start().return_value


@pytest.fixture
def message_service(port) -> MessageService:
    message_repo = MessageService(port)
    return message_repo


@pytest.mark.anyio
class TestEventsMessageService:
    subscriber_name = "subscriber_1"
    message = Message(
        publisher_name="live_message",
        ts=datetime(2023, 11, 3, 12, 34, 56, 789012),
        realm="udm",
        topic="topic_name",
        body={
            "foo": "bar",
            "foo1": "bar1",
        },
    )
    flat_message = {
        "publisher_name": "live_message",
        "ts": "2023-11-03T12:34:56.789012",
        "realm": "udm",
        "topic": "topic_name",
        "body": '{"foo": "bar", "foo1": "bar1"}',
    }

    async def test_add_live_message(self, message_service: MessageService):
        data = NewMessage(
            realm="udm", topic="topic_name", body={"foo": "bar", "foo1": "bar1"}
        )

        message_service._port.add_live_message = AsyncMock()

        await message_service.publish_message(data, "live_message", self.message.ts)

        message_service._port.add_live_message.assert_called_once_with(self.message)
