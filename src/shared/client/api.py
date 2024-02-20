# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any, Dict, List, Optional

import aiohttp

from app.consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from app.consumer.messages.api import v1_prefix as messages_api_prefix
from shared.models import (
    MQMessage,
    Subscription,
    MessageProcessingStatus,
    MessageProcessingStatusReport,
    Event,
)


class AsyncClient:
    def __init__(self, base_url, username: str, password: str):
        self.base_url = base_url
        self.auth = aiohttp.BasicAuth(username, password)

    async def cancel_subscription(self, name: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}",
                auth=self.auth,
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> Subscription:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}",
                auth=self.auth,
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
                auth=self.auth,
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
                auth=self.auth,
            ):
                # either return nothing or let `.post` throw
                pass

    async def submit_message(
        self, realm: str, topic: str, body: Dict[str, Any], name: str
    ):
        message = Event(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}{subscriptions_api_prefix}/subscriptions/{name}/messages-status",
                json=message.model_dump(),
                auth=self.auth,
            ):
                # either return nothing or let `.post` throw
                pass
