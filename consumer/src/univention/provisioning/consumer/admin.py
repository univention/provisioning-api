# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Client for the subscription administration routes of the Provisioning API."""

import enum
import logging
from urllib.parse import urljoin

import aiohttp
from pydantic import TypeAdapter

from univention.provisioning.models.subscription import NewSubscription, Subscription

logger = logging.getLogger(__name__)

_subscriptions_adapter = TypeAdapter(list[Subscription])

# Enough of an error body to explain it, without flooding the Job log.
_MAX_BODY_LENGTH = 1000


class ProvisioningApiError(Exception):
    def __init__(self, status: int, body: str):
        super().__init__(f"HTTP {status}: {body}")
        self.status = status
        self.body = body


class SubscriptionConflict(ProvisioningApiError):
    """The subscription exists with a different password or configuration."""


class SubscriptionCreation(enum.Enum):
    CREATED = "created"
    UNCHANGED = "unchanged"


class AdminClient:
    def __init__(self, base_url: str, username: str, password: str, timeout: float = 30):
        self.subscriptions_url = urljoin(base_url.strip("/") + "/", "v1/subscriptions")
        self.session = aiohttp.ClientSession(
            headers={"Authorization": aiohttp.encode_basic_auth(username, password)},
            timeout=aiohttp.ClientTimeout(total=timeout),
        )

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def create_subscription(self, subscription: NewSubscription) -> SubscriptionCreation:
        """
        Register a subscription.

        :raises SubscriptionConflict: The subscription exists with a different password or configuration.
        :raises ProvisioningApiError: Any other answer than 200 or 201.
        """
        logger.debug("Creating subscription: %r", subscription.model_dump(exclude={"password"}))
        async with self.session.post(self.subscriptions_url, json=subscription.model_dump()) as response:
            if response.status == 201:
                return SubscriptionCreation.CREATED
            if response.status == 200:
                return SubscriptionCreation.UNCHANGED
            body = (await response.text())[:_MAX_BODY_LENGTH]
            if response.status == 409:
                raise SubscriptionConflict(response.status, body)
            raise ProvisioningApiError(response.status, body)

    async def get_subscriptions(self) -> list[Subscription]:
        async with self.session.get(self.subscriptions_url) as response:
            if response.status != 200:
                raise ProvisioningApiError(response.status, (await response.text())[:_MAX_BODY_LENGTH])
            return _subscriptions_adapter.validate_python(await response.json())
