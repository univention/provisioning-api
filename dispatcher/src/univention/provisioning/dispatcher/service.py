# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging

from univention.provisioning.backends.message_queue import Empty, MessageAckManager, QueueStatus
from univention.provisioning.backends.nats_mq import ConsumerQueue, IncomingQueue
from univention.provisioning.models.message import Message, MQMessage
from univention.provisioning.models.subscription import Subscription

from .mq_port import MessageQueuePort
from .subscriptions_port import SubscriptionsPort

logger = logging.getLogger(__name__)


class DispatcherService:
    def __init__(
        self,
        ack_manager: MessageAckManager,
        mq_pull: MessageQueuePort,
        mq_push: MessageQueuePort,
        subscriptions: SubscriptionsPort,
    ):
        self.ack_manager = ack_manager
        self.mq_pull = mq_pull
        self.mq_push = mq_push
        self.subscriptions_db = subscriptions
        self._subscriptions: dict[str, dict[str, set[Subscription]]] = {}  # {realm: {topic: {Subscription, ..}}}

    async def run(self):
        logger.info("Storing event in consumer queues")
        queue_type = IncomingQueue(self.mq_pull.settings.nats_consumer_name)
        status = await self.mq_pull.initialize_subscription(queue_type, migrate_stream=True)

        # Initially fill self._subscriptions before starting to handle messages.
        await self.update_subscriptions_mapping()

        async with asyncio.TaskGroup() as task_group:
            # Background task that that informs about changes to the subscription data in the KV store.
            task_group.create_task(
                self.subscriptions_db.watch_for_subscription_changes(self.update_subscriptions_mapping)
            )
            task_group.create_task(self.dispatch_events(queue_type, status))

    async def dispatch_events(self, queue_type: IncomingQueue, migration_status: QueueStatus):
        while True:
            logger.debug("Waiting for an event...")
            try:
                message, acknowledgements = await self.mq_pull.get_one_message(timeout=10)
            except Empty:
                if migration_status == QueueStatus.READY:
                    logger.debug("No new dispatcher messages found in the incoming queue, continuing to wait.")
                    continue

                # Stream is sealed for migration - attempt to complete
                logger.info("No messages in sealed stream, completing migration")
                migration_status = await self.mq_pull.initialize_subscription(queue_type, migrate_stream=True)
                if migration_status == QueueStatus.READY:
                    logger.info("Stream migration completed, resuming normal operation")
                continue

            message_handler = self.handle_message(message)
            try:
                await self.ack_manager.process_message_with_ack_wait_extension(
                    message_handler, acknowledgements.acknowledge_message_in_progress
                )
                await acknowledgements.acknowledge_message()
            except Exception:
                try:
                    await acknowledgements.acknowledge_message_negatively()
                except Exception:
                    logger.error("Failed to negatively acknowledge message: %s", message)

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

        logger.debug("Found subscriptions: %r", subscriptions)

        for sub in subscriptions:
            logger.info("Sending message to %r", sub.name)
            try:
                await self.mq_push.enqueue_message(ConsumerQueue(sub.name), validated_msg)
            except Exception:
                logger.fatal("Failed to send message to %r", sub.name)
                await asyncio.sleep(1)
                raise

        if not subscriptions:
            logger.info("No consumers for message with realm: %r topic: %r.", validated_msg.realm, validated_msg.topic)

    async def update_subscriptions_mapping(self, *args, **kwargs) -> None:
        logger.info("Updating subscriptions mapping...")

        new_subscriptions_mapping: dict[str, dict[str, set[Subscription]]] = {}
        async for sub in self.subscriptions_db.get_all_subscriptions():
            logger.debug("Processing subscription: %r", sub.name)
            if not await self.mq_push.stream_exists(ConsumerQueue(sub.name)):
                logger.debug("Stream does not exist for subscription %r. Ignoring subscription", sub.name)
                continue
            for realm_topic in sub.realms_topics:
                new_subscriptions_mapping.setdefault(realm_topic.realm, {}).setdefault(realm_topic.topic, set()).add(
                    sub
                )

        self._subscriptions = new_subscriptions_mapping

        logger.info(
            "Subscriptions mapping updated: %r",
            {r: {t: {_s.name for _s in s} for t, s in v.items()} for r, v in self._subscriptions.items()},
        )
