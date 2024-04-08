# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch, call

import aiohttp
import pytest

from client import MessageHandler, AsyncClient
from shared.models import Message
from tests.conftest import SUBSCRIPTION_NAME, PROVISIONING_MESSAGE


@pytest.fixture
def async_client() -> AsyncMock:
    yield patch("src.client.api.AsyncClient").start().return_value


@pytest.mark.anyio
class TestMessageHandler:
    @staticmethod
    async def callback(result: list, message: Message):
        result.append(message)

    async def test_no_callback_function_provided(self, async_client: AsyncClient):
        with pytest.raises(ValueError, match="Callback functions can't be empty"):
            await MessageHandler(
                async_client, SUBSCRIPTION_NAME, [], message_limit=1
            ).run()

    async def test_get_one_message(self, async_client: AsyncClient):
        async_client.get_subscription_messages = AsyncMock(
            return_value=[PROVISIONING_MESSAGE]
        )
        async_client.set_message_status = AsyncMock()
        result = []

        await MessageHandler(
            async_client,
            SUBSCRIPTION_NAME,
            [lambda message: self.callback(result, message)],
            message_limit=1,
        ).run()

        async_client.get_subscription_messages.assert_called_once_with(
            SUBSCRIPTION_NAME, count=1, timeout=10
        )
        async_client.set_message_status.assert_called_once()
        assert len(result) == 1

    async def test_get_multiple_messages(self, async_client: AsyncClient):
        async_client.get_subscription_messages = AsyncMock(
            side_effect=[
                [PROVISIONING_MESSAGE],
                [PROVISIONING_MESSAGE],
                [PROVISIONING_MESSAGE],
            ]
        )
        async_client.set_message_status = AsyncMock()
        result = []

        await MessageHandler(
            async_client,
            SUBSCRIPTION_NAME,
            [lambda message: self.callback(result, message)],
            message_limit=3,
        ).run()

        async_client.get_subscription_messages.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, count=1, timeout=10),
                call(SUBSCRIPTION_NAME, count=1, timeout=10),
                call(SUBSCRIPTION_NAME, count=1, timeout=10),
            ]
        )
        assert async_client.set_message_status.call_count == 3

        assert len(result) == 3

    async def test_failed_to_acknowledge_message(self, async_client: AsyncClient):
        async_client.get_subscription_messages = AsyncMock(
            return_value=[PROVISIONING_MESSAGE]
        )
        async_client.set_message_status = AsyncMock(side_effect=aiohttp.ClientError)
        result = []

        await MessageHandler(
            async_client,
            SUBSCRIPTION_NAME,
            [lambda message: self.callback(result, message)],
            message_limit=1,
        ).run()

        async_client.get_subscription_messages.assert_called_once_with(
            SUBSCRIPTION_NAME, count=1, timeout=10
        )
        async_client.set_message_status.assert_called_once()
        assert len(result) == 1
