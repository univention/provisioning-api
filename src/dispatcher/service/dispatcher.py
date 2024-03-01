# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

from src.dispatcher.port import DispatcherPort
from shared.models import Message


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    async def dispatch_events(self):
        self._logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue("incoming", "dispatcher-service")
        while True:
            self._logger.info("Waiting for the event...")
            message = await self._port.wait_for_event()
            await self._port.acknowledge_message_in_progress(message)

            try:
                self._logger.info("Received message with content: %s", message.data)
                validated_msg = Message.model_validate(message.data)

                subscriptions = await self._port.get_realm_topic_subscriptions(
                    f"{validated_msg.realm}:{validated_msg.topic}"
                )

                for sub in subscriptions:
                    self._logger.info("Sending message to '%s'", sub)
                    await self._port.send_message_to_subscription(sub, validated_msg)

            except Exception as exc:
                self._logger.error("Failed to dispatch the event: %s", exc)

                await self._port.acknowledge_message_negatively(
                    message
                )  # TODO: handle failed events

            else:
                await self._port.acknowledge_message(message)
