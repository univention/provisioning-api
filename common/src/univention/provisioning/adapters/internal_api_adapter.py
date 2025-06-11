# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import aiohttp

from univention.provisioning.models.message import Message
from univention.provisioning.rest.models import FillQueueStatus, FillQueueStatusReport


class InternalAPIAdapter:
    """
    Client for the Internal REST API.
    """

    def __init__(self, url: str, username: str, password: str):
        self.base_url = url.rstrip("/")

        self.auth = aiohttp.BasicAuth(username, password)
        self.headers = [("accept", "application/json")]
        self._session = None

    async def connect(self):
        if not self._session:
            self._session = aiohttp.ClientSession(auth=self.auth, headers=self.headers, raise_for_status=True)

    async def close(self):
        if self._session:
            await self._session.close()

    async def update_subscription_queue_status(self, name: str, queue_status: FillQueueStatus) -> None:
        async with self._session.patch(
            f"{self.base_url}/v1/subscriptions/{name}/prefill",
            json=FillQueueStatusReport(status=queue_status.value).model_dump(),
        ):
            pass

    async def send_event(self, message: Message):
        async with self._session.post(f"{self.base_url}/v1/messages", json=message.model_dump()):
            pass
