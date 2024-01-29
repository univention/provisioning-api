# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
from typing import Any, Dict, List, Tuple

import aiohttp

import shared.models.api


class AsyncClient:
    def __init__(self, base_url):
        self.base_url = base_url

    async def create_subscription(
        self, name: str, realms_topics: List[List[str]], fill_queue: bool = False
    ):
        subscriber = shared.models.api.NewSubscriber(
            name=name, realms_topics=realms_topics, fill_queue=fill_queue
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            print(subscriber.model_dump())
            async with session.post(
                f"{self.base_url}/v1/subscriptions", json=subscriber.model_dump()
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self, name: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(f"{self.base_url}/v1/subscriptions/{name}"):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> shared.models.subscriber.Subscriber:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}/v1/subscriptions/{name}"
            ) as response:
                data = await response.json()
                return shared.models.api.Subscriber.model_validate(data)

    async def get_subscription_messages(
        self, name: str, count=None, first=None, last=None
    ) -> List[Tuple[str, shared.models.queue.Message]]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}/v1/subscriptions/{name}/messages",
                params=dict(count=count, first=first, last=last),
            ) as response:
                msgs = await response.json()
                return [shared.models.api.Message.model_validate(msg) for msg in msgs]

    async def set_message_status(
        self,
        name: str,
        message_id: str,
        status: shared.models.api.MessageProcessingStatus,
    ):
        report = shared.models.api.MessageProcessingStatusReport(status=status)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}/v1/subscriptions/{name}/messages/{message_id}",
                json=report.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[shared.models.subscriber.Subscriber]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(f"{self.base_url}/v1/subscriptions") as response:
                data = await response.json()
                return shared.models.api.Subscriber.model_validate(data)

    async def submit_message(self, realm: str, topic: str, body: Dict[str, Any]):
        message = shared.models.api.Event(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}/v1/messages", json=message.model_dump()
            ):
                # either return nothing or let `.post` throw
                pass

    @contextlib.asynccontextmanager
    async def stream(self, name: str):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                f"{self.base_url}/v1/subscriptions/{name}/ws"
            ) as websocket:
                yield AsyncClientStream(websocket)


class AsyncClientStream:
    def __init__(self, websocket: aiohttp.ClientWebSocketResponse):
        self.websocket = websocket

    async def receive_message(self) -> shared.models.queue.Message:
        data = await self.websocket.receive_json()
        return shared.models.queue.Message.model_validate(data)

    async def send_report(self, status: shared.models.api.MessageProcessingStatus):
        report = shared.models.api.MessageProcessingStatusReport(status=status)
        await self.websocket.send_json(report.model_dump())
