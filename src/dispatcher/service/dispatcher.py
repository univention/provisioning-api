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
        self._logger = logging.getLogger(__name__)

    async def dispatch_events(self):
        self._logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue("incoming")
        while True:
            self._logger.info("Waiting for the event...")
            msg = await self._port.wait_for_event()
            await msg.in_progress()

            try:
                data = json.loads(msg.data)
                validated_msg = Message.model_validate(data)
                self._logger.info("Received message with content: %s", data)

                subscribers = await self._port.get_realm_topic_subscribers(
                    f"{validated_msg.realm}:{validated_msg.topic}"
                )

                for sub in subscribers:
                    self._logger.info("Sending message to '%s'", sub["name"])
                    await self._port.send_event_to_consumer_queue(
                        sub["name"], validated_msg
                    )
            except Exception as exc:
                self._logger.error("Failed to dispatch the event: %s", exc)

                await msg.nak()  # TODO: handle failed events

            else:
                await msg.ack()
