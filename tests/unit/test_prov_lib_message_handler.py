# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, call, patch

import aiohttp
import pytest

from univention.provisioning.consumer import MessageHandler, ProvisioningConsumerClient
from univention.provisioning.models import Message

from ..mock_data import PROVISIONING_MESSAGE, SUBSCRIPTION_NAME


@pytest.fixture
def async_client() -> AsyncMock:
    yield patch("univention.provisioning.consumer.api.ProvisioningConsumerClient").start().return_value


@pytest.mark.anyio
@pytest.mark.provisioning_lib
class TestMessageHandler:
    @staticmethod
    async def callback(result: list, message: Message):
        result.append(message)

    async def test_no_callback_function_provided(self, async_client: ProvisioningConsumerClient):
        with pytest.raises(ValueError, match="Callback functions can't be empty"):
            await MessageHandler(async_client, [], message_limit=1).run()

    async def test_get_one_message(self, async_client: ProvisioningConsumerClient):
        async_client.get_subscription_message = AsyncMock(return_value=PROVISIONING_MESSAGE)
        async_client.set_message_status = AsyncMock()
        result = []

        async_client.settings.provisioning_api_username = SUBSCRIPTION_NAME
        await MessageHandler(
            async_client,
            [lambda message: self.callback(result, message)],
            message_limit=1,
        ).run()

        async_client.get_subscription_message.assert_called_once_with(SUBSCRIPTION_NAME, timeout=10)
        async_client.set_message_status.assert_called_once()
        assert len(result) == 1

    async def test_get_multiple_message(self, async_client: ProvisioningConsumerClient):
        async_client.get_subscription_message = AsyncMock(
            side_effect=[
                PROVISIONING_MESSAGE,
                PROVISIONING_MESSAGE,
                PROVISIONING_MESSAGE,
            ]
        )
        async_client.set_message_status = AsyncMock()
        result = []

        async_client.settings.provisioning_api_username = SUBSCRIPTION_NAME
        await MessageHandler(
            async_client,
            [lambda message: self.callback(result, message)],
            message_limit=3,
        ).run()

        async_client.get_subscription_message.assert_has_calls(
            [
                call(SUBSCRIPTION_NAME, timeout=10),
                call(SUBSCRIPTION_NAME, timeout=10),
                call(SUBSCRIPTION_NAME, timeout=10),
            ]
        )
        assert async_client.set_message_status.call_count == 3

        assert len(result) == 3

    @patch("asyncio.sleep", return_value=None)
    async def test_failed_to_acknowledge_message(self, mock_sleep, async_client: ProvisioningConsumerClient):
        async_client.get_subscription_message = AsyncMock(return_value=PROVISIONING_MESSAGE)
        async_client.set_message_status = AsyncMock(side_effect=aiohttp.ClientError)
        result = []

        async_client.settings.provisioning_api_username = SUBSCRIPTION_NAME
        await MessageHandler(
            async_client,
            [lambda message: self.callback(result, message)],
            message_limit=1,
        ).run()

        async_client.get_subscription_message.assert_called_once_with(SUBSCRIPTION_NAME, timeout=10)
        assert async_client.set_message_status.call_count == 4
        assert len(result) == 1
        assert mock_sleep.call_count == 3
