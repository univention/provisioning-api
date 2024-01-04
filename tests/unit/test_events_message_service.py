# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch
import pytest

from ..conftest import MESSAGE
from events.service import EventsService


@pytest.fixture
def port() -> AsyncMock:
    return patch("events.service.events.EventsPort").start().return_value


@pytest.fixture
def message_service(port) -> EventsService:
    message_repo = EventsService(port)
    return message_repo


@pytest.mark.anyio
class TestEventsMessageService:
    async def test_add_live_message(self, message_service: EventsService):
        message_service._port.add_live_event = AsyncMock()

        await message_service.publish_event(MESSAGE)
        message_service._port.add_live_event.assert_called_once_with(MESSAGE)
