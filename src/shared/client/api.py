# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any, Dict, List, Optional

import aiohttp

import logging

import shared.models.api
from shared.models.queue import MQMessage

from shared.client.config import settings

logger = logging.getLogger(__file__)


# TODO: the subscription part will be delegated to an admin using an admin API
class AsyncClient:
    async def create_subscriptions(
        self, name: str, realms_topics: List[str], request_prefill: bool = False
    ):
        logger.info("creating subscriptions for %s", str(realms_topics))
        for realm_topic in realms_topics:
            await self.create_subscription(
                name, realm_topic.split(":"), request_prefill
            )

    async def create_subscription(
        self, name: str, realm_topic: List[str], request_prefill: bool = False
    ):
        subscriber = shared.models.api.NewSubscriber(
            name=name, realm_topic=realm_topic, request_prefill=request_prefill
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            # TODO: do this with propper logging
            print(subscriber.model_dump())
            async with session.post(
                f"{settings.consumer_registration_url}/subscriptions",
                json=subscriber.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self, name: str, realm: str, topic: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(
                f"{settings.consumer_registration_url}/subscriptions/{name}",
                params={"realm": realm, "topic": topic},
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> shared.models.subscriber.Subscriber:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_registration_url}/subscriptions/{name}"
            ) as response:
                data = await response.json()
                return shared.models.subscriber.Subscriber.model_validate(data)

    async def get_subscription_messages(
        self,
        name: str,
        count: Optional[int] = None,
        timeout: Optional[float] = None,
        pop: Optional[bool] = None,
        force: Optional[bool] = None,
    ) -> List[shared.models.queue.MQMessage]:
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
                return [
                    shared.models.queue.MQMessage.model_validate(msg) for msg in msgs
                ]

    async def set_message_status(
        self,
        name: str,
        message: MQMessage,
        status: shared.models.api.MessageProcessingStatus,
    ):
        report = shared.models.api.MessageProcessingStatusReport(status=status)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{settings.consumer_messages_url}/subscriptions/{name}/messages/",
                json={"msg": message.model_dump(), "report": report.model_dump()},
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[shared.models.subscriber.Subscriber]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_registration_url}/subscriptions"
            ) as response:
                data = await response.json()
                # TODO: parse a list of subscriptions instead
                return [shared.models.subscriber.Subscriber.model_validate(data)]

    async def submit_message(self, realm: str, topic: str, body: Dict[str, Any]):
        message = shared.models.api.Event(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{settings.consumer_registration_url}/messages",
                json=message.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass
