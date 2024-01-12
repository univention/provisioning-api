# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging

from shared.models import FillQueueStatus
from src.dispatcher.port import DispatcherPort
from shared.models.queue import Message


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def send_event(self, subscriber: dict, new_msg: Message):
        if subscriber["fill_queue_status"] in (
            FillQueueStatus.done,
            FillQueueStatus.failed,
        ):
            self.logger.info("Sending message to %s", subscriber["name"])
            await self._port.send_event_to_consumer_queue(subscriber["name"], new_msg)
        else:
            self.logger.info(
                "Sending message to incoming queue for subscriber '%s' due to a temporary lock on its queue.",
                subscriber["name"],
            )
            new_msg.destination = subscriber["name"]
            await self._port.send_event_to_incoming_queue(new_msg)

    async def dispatch_event(self):
        self.logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue("incoming")
        while True:
            self.logger.info("Waiting for the event...")

            msg = await self._port.wait_for_event()
            new_msg = Message.model_validate(json.loads(msg.data))
            realm = new_msg.realm
            topic = new_msg.topic
            self.logger.info("Received message: %s", new_msg)

            subscribers = []
            if new_msg.destination == "*":
                subscribers = await self._port.get_realm_topic_subscribers(
                    f"{realm}:{topic}"
                )
            else:
                subscriber = await self._port.get_subscriber(new_msg.destination)
                subscribers.append(subscriber)

            for subscriber in subscribers:
                await self.send_event(subscriber, new_msg)
