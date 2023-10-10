import contextlib
from typing import Any, Dict, List

import aiohttp

import core.models.api


class AsyncClient:
    def __init__(self, base_url):
        self.base_url = base_url

    async def create_subscription(
        self, name: str, realms_topics: List[List[str]], fill_queue: bool = False
    ):
        subscriber = core.models.api.NewSubscriber(
            name=name, realms_topics=realms_topics, fill_queue=fill_queue
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}/v1/subscription", json=subscriber.model_dump()
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self, name: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(f"{self.base_url}/v1/subscription/{name}"):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> core.models.subscriber.Subscriber:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}/v1/subscription/{name}"
            ) as response:
                data = await response.json()
                return core.models.subscriber.Subscriber.model_validate(data)

    async def get_subscription_messages(
        self, name: str, count=None, first=None, last=None
    ) -> List[core.models.queue.Message]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.base_url}/v1/subscription/{name}/message",
                params=dict(count=count),
            ) as response:
                msgs = await response.json()
                return [
                    core.models.queue.Message.model_validate(msg[1]) for msg in msgs
                ]

    async def set_message_status(
        self,
        name: str,
        message_id: str,
        status: core.models.api.MessageProcessingStatus,
    ):
        report = core.models.api.MessageProcessingStatusReport(status=status)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}/v1/subscription/{name}/message/{message_id}",
                json=report.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[core.models.subscriber.Subscriber]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(f"{self.base_url}/v1/subscription/") as response:
                data = await response.json()
                return [core.models.subscriber.Subscriber.model_validate(data)]

    async def submit_message(self, realm: str, topic: str, body: Dict[str, Any]):
        message = core.models.api.NewMessage(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.base_url}/v1/message", json=message.model_dump()
            ):
                # either return nothing or let `.post` throw
                pass

    @contextlib.asynccontextmanager
    async def stream(self, name: str):
        async with aiohttp.ClientSession() as session:
            async with session.ws_connect(
                f"{self.base_url}/v1/subscription/{name}/ws"
            ) as websocket:
                yield AsyncClientStream(websocket)


class AsyncClientStream:
    def __init__(self, websocket: aiohttp.ClientWebSocketResponse):
        self.websocket = websocket

    async def receive_message(self) -> core.models.queue.Message:
        data = await self.websocket.receive_json()
        return core.models.queue.Message.model_validate(data)

    async def send_report(self, status: core.models.api.MessageProcessingStatus):
        report = core.models.api.MessageProcessingStatusReport(status=status)
        await self.websocket.send_json(report.model_dump())
