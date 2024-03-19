# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging
from typing import Dict

from shared.utils.message_ack_manager import MessageAckManager
from src.dispatcher.port import DispatcherPort
from shared.models import MQMessage, Message, Bucket


class DispatcherService:
    DISPATCHER_QUEUE = "incoming"

    def __init__(self, port: DispatcherPort):
        self._port = port
        self.ack_manager = MessageAckManager()
        self.subscriptions: Dict[str, list] = {}
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    async def dispatch_events(self):
        self._logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue(self.DISPATCHER_QUEUE, "dispatcher-service")
        asyncio.create_task(
            self._port.watch_for_changes(self.subscriptions, Bucket.subscriptions)
        )

        while True:
            self._logger.info("Waiting for the event...")
            message = await self._port.wait_for_event()
            await self.ack_manager.process_message_with_ack_wait_extension(
                message, self.handle_message, self._port.acknowledge_message_in_progress
            )

    async def handle_message(self, message: MQMessage):
        self._logger.info("Received message with content: %s", message.data)
        validated_msg = Message.model_validate(message.data)

        subscriptions = (
            self.subscriptions.get(f"{validated_msg.realm}:{validated_msg.topic}") or []
        )

        for sub in subscriptions:
            self._logger.info("Sending message to '%s'", sub)
            await self._port.send_message_to_subscription(sub, validated_msg)

        await self._port.acknowledge_message(message)
