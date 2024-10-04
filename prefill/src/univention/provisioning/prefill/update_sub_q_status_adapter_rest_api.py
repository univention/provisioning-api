# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import aiohttp

from univention.provisioning.rest.models import FillQueueStatus, FillQueueStatusReport

from .update_sub_q_status_port import UpdateSubscriptionsQueueStatusPort


class SubscriptionsRestApiAdapter(UpdateSubscriptionsQueueStatusPort):
    """Update the subscription queue status through the Subscription REST API."""

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

    async def update_subscription_queue_status(self, name: str, queue_status: FillQueueStatus) -> None:
        async with self._session.patch(
            f"{self._url}/v1/subscriptions/{name}/prefill",
            json=FillQueueStatusReport(status=queue_status.value).model_dump(),
        ):
            pass
