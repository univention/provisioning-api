# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging

from univention.provisioning.models.constants import DISPATCHER_STREAM, DISPATCHER_SUBJECT_TEMPLATE
from univention.provisioning.models.message import Message, MQMessage
from univention.provisioning.models.subscription import Subscription
from univention.provisioning.utils.message_ack_manager import MessageAckManager

from .port import DispatcherPort

logger = logging.getLogger(__name__)


class DispatcherService:
    def __init__(self, port: DispatcherPort):
        self._port = port
        self.ack_manager = MessageAckManager()
        self._subscriptions: dict[str, dict[str, set[Subscription]]] = {}  # {realm: {topic: {Subscription, ..}}}

    async def dispatch_events(self):
        logger.info("Storing event in consumer queues")
        await self._port.subscribe_to_queue(DISPATCHER_STREAM, "dispatcher-service")

        # Initially fill self._subscriptions before starting to handle messages.
        await self.update_subscriptions_mapping()

        async with asyncio.TaskGroup() as task_group:
            # Background task that that informs about changes to the subscription data in the KV store.
            task_group.create_task(self._port.watch_for_subscription_changes(self.update_subscriptions_mapping))

            while True:
                logger.debug("Waiting for an event...")
                message = await self._port.wait_for_event()
                message_handler = self.handle_message(message)
                acknowledge_message_in_progress = lambda: self._port.acknowledge_message_in_progress(message)  # noqa: E731
                await task_group.create_task(
                    self.ack_manager.process_message_with_ack_wait_extension(
                        message_handler, acknowledge_message_in_progress
                    )
                )

    async def handle_message(self, message: MQMessage):
        data = message.data
        if data.get("realm") == "udm":
            old = data.get("body", {}).get("old", {})
            new = data.get("body", {}).get("new", {})
            dn = new.get("dn") or old.get("dn")
            details = f"DN: {dn!r} "
        else:
            details = ""
        logger.info(
            "Received message to handle (%sPublisher: %r Realm: %r Topic: %r TS: %s).",
            details,
            data.get("publisher_name"),
            data.get("realm"),
            data.get("topic"),
            data.get("ts"),
        )
        logger.debug("Message content: %r", data)

        validated_msg = Message.model_validate(data)

        subscriptions = self._subscriptions.get(validated_msg.realm, {}).get(validated_msg.topic, [])

        for sub in subscriptions:
            logger.info("Sending message to %r", sub.name)
            await self._port.send_message_to_subscription(
                sub.name, DISPATCHER_SUBJECT_TEMPLATE.format(subscription=sub.name), validated_msg
            )
        if not subscriptions:
            logger.info("No consumers for message with realm: %r topic: %r.", validated_msg.realm, validated_msg.topic)

        await self._port.acknowledge_message(message)

    async def update_subscriptions_mapping(self, *args, **kwargs) -> None:
        new_subscriptions_mapping: dict[str, dict[str, set[Subscription]]] = {}
        async for sub in self._port.get_all_subscriptions():
            for realm_topic in sub.realms_topics:
                new_subscriptions_mapping.setdefault(realm_topic.realm, {}).setdefault(realm_topic.topic, set()).add(
                    sub
                )
        self._subscriptions = new_subscriptions_mapping
        logger.info(
            "Subscriptions mapping updated: %r",
            {r: {t: {_s.name for _s in s} for t, s in v.items()} for r, v in self._subscriptions.items()},
        )
