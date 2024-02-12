# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any, Dict, List, Optional, Tuple

import aiohttp

from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.messages.api import v1_prefix as messages_api_prefix
from shared.models import (
    MQMessage,
    Subscription,
    NewSubscription,
    MessageProcessingStatus,
    MessageProcessingStatusReport,
    Event,
)


class AsyncClient:
    def __init__(self, base_url):
        self.base_url = base_url

    async def create_subscription(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        request_prefill: bool = False,
    ):
        subscriber = NewSubscription(
            name=name, realms_topics=realms_topics, request_prefill=request_prefill
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            # TODO: do this with propper logging
            print(subscriber.model_dump())
            async with session.post(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions",
                json=subscriber.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self, name: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}",
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> Subscription:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}"
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
    ) -> List[MQMessage]:
        _params = {
            "count": count,
            "timeout": timeout,
            "pop": pop,
            "force": force,
        }
        params = {k: v for k, v in _params.items() if v is not None}

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}{messages_api_prefix}/subscriptions/{name}/messages",
                params=params,
            ) as response:
                msgs = await response.json()
                return [MQMessage.model_validate(msg) for msg in msgs]

    async def set_message_status(
        self,
        name: str,
        message: MQMessage,
        status: MessageProcessingStatus,
    ):
        report = MessageProcessingStatusReport(status=status)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}{messages_api_prefix}/subscriptions/{name}/messages/",
                json={"msg": message.model_dump(), "report": report.model_dump()},
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[Subscription]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions"
            ) as response:
                data = await response.json()
                # TODO: parse a list of subscriptions instead
                return [Subscription.model_validate(data)]

    async def submit_message(
        self, realm: str, topic: str, body: Dict[str, Any], name: str
    ):
        message = Event(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}/messages-status",
                json=message.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass
