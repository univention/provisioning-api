# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

import aiohttp

from univention.provisioning.models import FillQueueStatus, Message

from ..config import settings


class InternalAPIAdapter:
    """
    Client for the Internal REST API.
    """

    def __init__(self, username: str, password: str):
        self.base_url = settings.internal_api_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.auth = aiohttp.BasicAuth(username, password)
        self.headers = [("accept", "application/json")]
        self._session = None
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        if not self._session:
            self._session = aiohttp.ClientSession(auth=self.auth, headers=self.headers, raise_for_status=True)

    async def close(self):
        if self._session:
            await self._session.close()

    async def update_subscription_queue_status(self, name: str, queue_status: FillQueueStatus) -> None:
        async with self._session.patch(
            f"{self.base_url}subscriptions/{name}?prefill_queue_status={queue_status.value}"
        ):
            pass

    async def send_event(self, message: Message):
        async with self._session.post(f"{self.base_url}events", json=message.model_dump()):
            pass
