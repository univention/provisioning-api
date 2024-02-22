# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

from shared.models import (
    Subscription,
    NewSubscription,
    Event,
    ProvisioningMessage,
    MessageProcessingStatusReport,
)

from shared.client.config import settings

logger = logging.getLogger(__file__)


# TODO: the subscription part will be delegated to an admin using an admin API
class AsyncClient:
    async def create_subscription(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        request_prefill: bool = False,
    ):
        logger.info("creating subscription for %s", str(realms_topics))
        subscription = NewSubscription(
            name=name, realms_topics=realms_topics, request_prefill=request_prefill
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            # TODO: do this with propper logging
            print(subscription.model_dump())
            async with session.post(
                f"{settings.consumer_registration_url}/subscriptions",
                json=subscription.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self, name: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(
                f"{settings.consumer_registration_url}/subscriptions/{name}",
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> Subscription:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_registration_url}/subscriptions/{name}"
            ) as response:
                data = await response.json()
                return Subscription.model_validate(data)

    async def get_subscription_messages(
        self,
        name: str,
        count: Optional[int] = None,
        timeout: Optional[float] = None,
        pop: Optional[bool] = None,
        force: Optional[bool] = None,
    ) -> List[ProvisioningMessage]:
        _params = {
            "count": count,
            "timeout": timeout,
            "pop": pop,
            "force": force,
        }
        params = {k: v for k, v in _params.items() if v is not None}

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_messages_url}/subscriptions/{name}/messages",
                params=params,
            ) as response:
                msgs = await response.json()
                return [ProvisioningMessage.model_validate(msg) for msg in msgs]

    async def set_message_status(
        self, name: str, reports: List[MessageProcessingStatusReport]
    ):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{settings.consumer_messages_url}/subscriptions/{name}/messages-status/",
                json=[report.model_dump() for report in reports],
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[Subscription]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_registration_url}/subscriptions"
            ) as response:
                data = await response.json()
                # TODO: parse a list of subscriptions instead
                return [Subscription.model_validate(data)]

    # FIXME: What is the purpose of this method? It looks like it wants to publish_event via Event API
    async def submit_message(
        self, realm: str, topic: str, body: Dict[str, Any], name: str
    ):
        message = Event(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{settings.consumer_registration_url}/messages",
                json=message.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass
