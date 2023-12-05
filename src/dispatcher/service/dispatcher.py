import asyncio
import json
import logging
from typing import List

from src.dispatcher.port import DispatcherPort
from shared.models.queue import NatsMessage, Message

logger = logging.getLogger(__name__)


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port

    async def retrieve_event_from_incoming_queue(
        self, timeout: float = 5, pop: bool = True
    ) -> List[NatsMessage]:
        return await self._port.retrieve_event_from_queue("incoming", timeout, pop)

    async def get_realm_topic_subscribers(self, realm_topic_str) -> List[str]:
        return await self._port.get_list_value(realm_topic_str)

    async def store_event_in_consumer_queues(self):
        print("Storing event in consumer queues")
        await self._port.subscribe_to_incoming_queue("incoming")

        try:
            while True:
                print("Waiting for the event...")
                msg = await self._port._nats_adapter._future
                data = json.loads(msg.data)
                realm = data["realm"]
                topic = data["topic"]
                print(f"Received message with content '{data}'")

                subscribers = await self.get_realm_topic_subscribers(f"{realm}:{topic}")
                print(f"{subscribers=}")

                for sub in subscribers:
                    print(f"Sending message to '{sub}'")
                    new_ms = Message.inflate(data)
                    await self._port.store_event_in_queue(sub, new_ms)

                self._port._nats_adapter._future = asyncio.Future()

        except Exception as err:
            print(err)


async def main():
    async with DispatcherPort.port_context() as port:
        service = DispatcherService(port)
        await service.store_event_in_consumer_queues()


if __name__ == "__main__":
    asyncio.run(main())
