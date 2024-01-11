# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
from typing import List

from shared.models import FillQueueStatus
from src.dispatcher.port import DispatcherPort
from shared.models.queue import NatsMessage, Message


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    async def retrieve_event_from_incoming_queue(
        self, timeout: float = 5, pop: bool = True
    ) -> List[NatsMessage]:
        return await self._port.retrieve_event_from_queue("incoming", timeout, pop)

    async def get_realm_topic_subscribers(self, realm_topic_str) -> List[str]:
        return await self._port.get_list_value(realm_topic_str)

    async def send_event(self, sub_name: str, new_msg: Message):
        sub_info = await self._port.get_subscriber(sub_name)
        if not sub_info:
            return
        if sub_info["fill_queue_status"] in (
            FillQueueStatus.done,
            FillQueueStatus.failed,
        ):
            self.logger.info("Sending message to %s", sub_name)
            await self._port.send_event_to_consumer_queue(sub_name, new_msg)
        else:
            self.logger.info(
                "Sending message to incoming queue for subscriber '%s' due to a temporary lock on its queue.",
                sub_name,
            )
            new_msg.destination = sub_name
            await self._port.send_event_to_incoming_queue(new_msg)

    async def store_event_in_consumer_queues(self):
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
                subscribers = await self.get_realm_topic_subscribers(
                    f"{realm}:{topic}"
                )  # TODO: add this method to Consumer REST API
            else:
                subscribers.append(new_msg.destination)

            for sub_name in subscribers:
                await self.send_event(sub_name, new_msg)
