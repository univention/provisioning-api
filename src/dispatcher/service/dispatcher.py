import json
import logging
from typing import List

from src.dispatcher.port import DispatcherPort
from shared.models.queue import NatsMessage, Message

logging.basicConfig(level=logging.INFO)
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
        logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue("incoming")
        while True:
            logger.info("Waiting for the event...")
            msg = await self._port.wait_for_event()

            data = json.loads(msg.data)
            realm = data["realm"]
            topic = data["topic"]
            logger.info(f"Received message with content '{data}'")

            subscribers = await self.get_realm_topic_subscribers(f"{realm}:{topic}")

            for sub in subscribers:
                logger.info(f"Sending message to '{sub}'")
                new_ms = Message.inflate(data)
                await self._port.store_event_in_queue(sub, new_ms)
