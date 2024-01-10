# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from types import TracebackType
from typing import Optional, Type

import aiohttp

from shared.models import Message


class EventAdapter:
    """
    Client for the Events REST API, providing the interfaces required by `UDMMessagingService`.

    It is intended to be used as an async context manager:
    ```
    async with EventAdapter("http://localhost:7777/events/v1", "username", "password") as adapter:
        await adapter.send_event(message)
    ```
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.auth = aiohttp.BasicAuth(username, password)
        self.headers = [("accept", "application/json")]
        self._session = None

    async def __aenter__(self) -> "EventAdapter":
        if not self._session:
            self._session = aiohttp.ClientSession(
                auth=self.auth, headers=self.headers, raise_for_status=True
            )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if self._session:
            await self._session.close()

    async def send_event(self, message: Message):
        async with self._session.post(
            f"{self.base_url}events/", json=message.flatten()
        ) as request:
            response = await request.json()
            return response
