# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import aiohttp

from univention.provisioning.models.message import Message

from .send_event_port import SendEventPort


class SubscriptionsRestApiAdapter(SendEventPort):
    """Send an event through the Subscription REST API."""

    def __init__(self, url: str, username: str, password: str):
        super().__init__(url=url, username=username, password=password)
        self._url = self._url.rstrip("/")
        self._auth = aiohttp.BasicAuth(username, password)
        self._headers = [("accept", "application/json")]
        self._session = None

    async def connect(self):
        if not self._session:
            self._session = aiohttp.ClientSession(auth=self._auth, headers=self._headers, raise_for_status=True)

    async def close(self):
        if self._session:
            await self._session.close()

    async def send_event(self, message: Message):
        async with self._session.post(f"{self._url}/v1/messages", json=message.model_dump()):
            pass
