# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging
from typing import Dict, List

from shared.utils.old_message_ack_manager import MessageAckManager
from server.core.dispatcher.port import DispatcherPort
from shared.models import (
    Message,
    MQMessage,
    DISPATCHER_STREAM,
    DISPATCHER_SUBJECT_TEMPLATE,
)


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        self.ack_manager = MessageAckManager()
        self._subscriptions: Dict[str, List[str]] = {}
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    async def dispatch_events(self):
        self._logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue(DISPATCHER_STREAM, "dispatcher-service")
        asyncio.create_task(self._port.watch_for_changes(self._subscriptions))

        while True:
            self._logger.info("Waiting for the event...")
            message = await self._port.wait_for_event()
            await self.ack_manager.process_message_with_ack_wait_extension(
                message, self.handle_message, self._port.acknowledge_message_in_progress
            )

    async def handle_message(self, message: MQMessage):
        self._logger.info("Received message with content: %s", message.data)
        validated_msg = Message.model_validate(message.data)

        subscriptions = self._subscriptions.get(
            f"{validated_msg.realm}:{validated_msg.topic}", []
        )

        for sub in subscriptions:
            self._logger.info("Sending message to '%s'", sub)
            await self._port.send_message_to_subscription(
                sub, DISPATCHER_SUBJECT_TEMPLATE.format(subscription=sub), validated_msg
            )

        await self._port.acknowledge_message(message)
