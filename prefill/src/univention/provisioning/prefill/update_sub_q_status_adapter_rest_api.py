# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

import aiohttp

from univention.provisioning.models.subscription import FillQueueStatusReport

from .update_sub_q_status_port import UpdateSubscriptionsQueueStatusPort

logger = logging.getLogger(__name__)


class SubscriptionsRestApiAdapter(UpdateSubscriptionsQueueStatusPort):
    """Update the subscription queue status through the Subscription REST API."""

    def __init__(self, url: str, username: str, password: str):
        super().__init__(url=url, username=username, password=password)
        self._url = self._url.rstrip("/")
        self._auth = aiohttp.BasicAuth(username, password)
        self._headers = [("accept", "application/json")]
        self._session = None

    async def __aenter__(self) -> UpdateSubscriptionsQueueStatusPort:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.close()
        return False

    async def connect(self):
        if not self._session:
            self._session = aiohttp.ClientSession(auth=self._auth, headers=self._headers, raise_for_status=True)

    async def close(self):
        if self._session:
            await self._session.close()

    async def update_subscription_queue_status(self, subscription_name, status):
        try:
            async with self._session.patch(
                f"{self._url}/v1/subscriptions/{subscription_name}/prefill",
                json=FillQueueStatusReport(status=status.value).model_dump(),
            ) as response:
                response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                # Subscription doesn't exist anymore - mark message as processed
                logger.warning(f"Subscription {subscription_name} not found, treating as processed")
                return
            raise
