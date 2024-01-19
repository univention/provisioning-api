# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging

from src.dispatcher.port import DispatcherPort
from shared.models.queue import Message


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def dispatch_events(self):
        self.logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue("incoming")
        while True:
            self.logger.info("Waiting for the event...")
            msg = await self._port.wait_for_event()

            data = json.loads(msg.data)
            realm = data["realm"]
            topic = data["topic"]
            self.logger.info(f"Received message with content: {data}")

            subscribers = await self._port.get_realm_topic_subscribers(
                f"{realm}:{topic}"
            )

            for sub in subscribers:
                self.logger.info("Sending message to '%s'", sub["name"])
                new_ms = Message.model_validate(data)
                await self._port.send_event_to_consumer_queue(sub["name"], new_ms)
