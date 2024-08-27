# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging
from typing import Dict, List

from server.core.dispatcher.port import DispatcherPort
from server.utils.old_message_ack_manager import MessageAckManager
from univention.provisioning.models import (
    DISPATCHER_STREAM,
    DISPATCHER_SUBJECT_TEMPLATE,
    Message,
    MQMessage,
)

logger = logging.getLogger(__name__)


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        self.ack_manager = MessageAckManager()
        self._subscriptions: Dict[str, List[str]] = {}

    async def dispatch_events(self):
        logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue(DISPATCHER_STREAM, "dispatcher-service")

        async with asyncio.TaskGroup() as task_group:
            task_group.create_task(self._port.watch_for_changes(self._subscriptions))

            while True:
                logger.debug("Waiting for an event...")
                message = await self._port.wait_for_event()
                await task_group.create_task(
                    self.ack_manager.process_message_with_ack_wait_extension(
                        message, self.handle_message, self._port.acknowledge_message_in_progress
                    )
                )

    async def handle_message(self, message: MQMessage):
        data = message.data
        logger.info(
            "Received message to handle (Publisher: %r Realm: %r Topic: %r TS: %s).",
            data.get("publisher_name"),
            data.get("realm"),
            data.get("topic"),
            data.get("ts"),
        )
        logger.debug("Message content: %r", data)

        validated_msg = Message.model_validate(data)

        subscriptions = self._subscriptions.get(f"{validated_msg.realm}:{validated_msg.topic}", [])

        for sub in subscriptions:
            logger.info("Sending message to %r", sub)
            await self._port.send_message_to_subscription(
                sub, DISPATCHER_SUBJECT_TEMPLATE.format(subscription=sub), validated_msg
            )

        await self._port.acknowledge_message(message)
