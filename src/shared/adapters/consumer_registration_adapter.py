# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

import aiohttp

from shared.config import settings
from shared.models import FillQueueStatus


class ConsumerRegistrationAdapter:
    """
    Client for the Consumer Registration REST API, providing the interfaces required by `DispatcherService`.
    ```
    """

    def __init__(self):
        self.base_url = settings.consumer_registration_url
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

    async def get_realm_topic_subscriptions(self, realm_topic: str) -> list[str]:
        async with self._session.get(
            f"{self.base_url}subscriptions/filter?realm_topic={realm_topic}"
        ) as request:
            return await request.json()

    async def update_subscription_queue_status(
        self, name: str, queue_status: FillQueueStatus
    ) -> None:
        async with self._session.patch(
            f"{self.base_url}subscriptions/{name}?prefill_queue_status={queue_status.value}"
        ):
            pass
