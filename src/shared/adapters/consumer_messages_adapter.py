# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

import aiohttp

from shared.config import settings
from shared.models import Message


class ConsumerMessagesAdapter:
    """
    Client for the Consumer Messages REST API`.
    ```
    """

    def __init__(self):
        self.base_url = settings.consumer_messages_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.auth = aiohttp.BasicAuth(
            settings.consumer_event_username, settings.consumer_event_password
        )
        self.headers = [("accept", "application/json")]
        self._session = None
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        if not self._session:
            self._session = aiohttp.ClientSession(
                auth=self.auth, headers=self.headers, raise_for_status=True
            )

    async def close(self):
        if self._session:
            await self._session.close()

    async def create_prefill_message(self, name: str, message: Message):
        async with self._session.post(
            f"{self.base_url}subscriptions/{name}/prefill-messages",
            json=message.model_dump(),
        ):
            pass

    async def create_prefill_stream(self, subscription_name: str):
        async with self._session.post(
            f"{self.base_url}subscriptions/{subscription_name}/prefill-stream",
        ):
            pass

    async def send_message(self, name: str, message: Message):
        async with self._session.post(
            f"{self.base_url}subscriptions/{name}/messages",
            json=message.model_dump(),
        ):
            pass
