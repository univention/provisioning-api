# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any, Dict, List, Optional

import aiohttp

import shared.models.api
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.messages.api import v1_prefix as messages_api_prefix
from shared.models.queue import QueueType


class AsyncClient:
    def __init__(self, base_url):
        self.base_url = base_url

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
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions",
                json=subscriber.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self, name: str, realm: str, topic: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}",
                params={"realm": realm, "topic": topic},
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> shared.models.subscriber.Subscriber:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}"
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
                f"{self.base_url}{messages_api_prefix}/subscriptions/{name}/messages",
                params=params,
            ) as response:
                msgs = await response.json()
                return [
                    shared.models.queue.MQMessage.model_validate(msg) for msg in msgs
                ]

    async def set_message_status(
        self,
        name: str,
        messages_seq_num: List[int],
        queue_type: QueueType,
        status: shared.models.api.MessageProcessingStatus,
    ):
        report = shared.models.api.MessageProcessingStatusReport(
            status=status, messages_seq_num=messages_seq_num, queue_type=queue_type
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}{messages_api_prefix}/subscriptions/{name}/messages/",
                json=report.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[shared.models.subscriber.Subscriber]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions"
            ) as response:
                data = await response.json()
                # TODO: parse a list of subscriptions instead
                return [shared.models.subscriber.Subscriber.model_validate(data)]

    async def submit_message(self, realm: str, topic: str, body: Dict[str, Any]):
        message = shared.models.api.Event(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}{subscriptions_api_prefix}/messages",
                json=message.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass
