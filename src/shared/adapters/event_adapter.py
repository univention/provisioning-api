# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import aiohttp

from shared.config import settings
from shared.models import Message


class EventAdapter:
    """
    Client for the Events REST API, providing the interfaces required by `UDMMessagingService`.
    ```
    """

    def __init__(self):
        self.base_url = settings.event_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.auth = aiohttp.BasicAuth(settings.event_username, settings.event_password)
        self.headers = [("accept", "application/json")]
        self._session = None

    async def connect(self):
        if not self._session:
            self._session = aiohttp.ClientSession(
                auth=self.auth, headers=self.headers, raise_for_status=True
            )

    async def close(self):
        if self._session:
            await self._session.close()

    async def send_event(self, message: Message):
        async with self._session.post(
            f"{self.base_url}events/", json=message.model_dump()
        ) as request:
            response = await request.json()
            return response
