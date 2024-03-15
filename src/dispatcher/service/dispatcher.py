# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging

from shared.utils.message_ack_manager import MessageAckManager
from src.dispatcher.port import DispatcherPort
from shared.models import Message, MQMessage


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        self.ack_manager = MessageAckManager()
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    async def dispatch_events(self):
        self._logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue("incoming", "dispatcher-service")
        while True:
            self._logger.info("Waiting for the event...")
            message = await self._port.wait_for_event()
            await self.ack_manager.process_message_with_ack_wait_extension(
                message, self.handle_message, self._port.acknowledge_message_in_progress
            )

    async def handle_message(self, message: MQMessage):
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

            # TODO: handle failed events
            await self._port.acknowledge_message_negatively(message)

        else:
            await self._port.acknowledge_message(message)
