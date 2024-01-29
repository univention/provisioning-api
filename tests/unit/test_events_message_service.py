# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock
import pytest

from ..conftest import MESSAGE
from events.service import EventsService


@pytest.fixture
def message_service() -> EventsService:
    return EventsService(AsyncMock())


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
class TestEventsMessageService:
    async def test_add_live_message(self, message_service: EventsService):
        await message_service.publish_event(MESSAGE)

        message_service._port.add_live_event.assert_called_once_with(MESSAGE)
