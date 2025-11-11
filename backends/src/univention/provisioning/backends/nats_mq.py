# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import json
import logging
import os
from typing import Any, Callable, Optional, Tuple

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig, DeliverPolicy, RetentionPolicy, StreamConfig
from nats.js.errors import NotFoundError, ServerError
from typing_extensions import Self

from univention.provisioning.models.message import BaseMessage, MQMessage, ProvisioningMessage

from .message_queue import Acknowledgements, Empty, MessageQueue, json_decoder, json_encoder

logger = logging.getLogger(__name__)


class BaseQueue:
    # the base queue name.
    # Used to construct the nats stream name and default subject
    name: str
    # nats durable consumer name
    _consumer_name: str | None = None
    # nats stream retention policy
    retention_policy: RetentionPolicy = RetentionPolicy.WORK_QUEUE
    deliver_policy: DeliverPolicy = DeliverPolicy.ALL
    # Nats stream replicas
    # Configures to how many nats instances the messages in a stream are replicated.
    replicas: int = 1
    # Nats stream subjects.
    # Nats allows the configuration of multiple subjects on one stream.
    subjects: list[str] | None = None

    @property
    def queue_name(self) -> str:
        return f"stream:{self.name}"

    @property
    def consumer_name(self) -> str:
        return f"durable_name:{self._consumer_name or self.name}"

    @property
    def message_subject(self) -> str:
        return self.name

    def stream_config(self) -> StreamConfig:
        return StreamConfig(
            name=self.queue_name,
            subjects=self.subjects or [self.message_subject],
            retention=self.retention_policy,
            # TODO: set to 3 after nats clustering is stable.
            num_replicas=self.replicas,
        )

    def consumer_config(self) -> ConsumerConfig:
        return ConsumerConfig(
            durable_name=self.consumer_name,
            max_ack_pending=1,
            deliver_policy=self.deliver_policy,
        )

    def __eq__(self, other) -> bool:
        return self.name == other.name and self.consumer_name == other.consumer_name


class ConsumerQueue(BaseQueue):
    """
    Writer: dispatcher
    Reader: provisioning consumers via the Provisioning API
    """

    retention_policy = RetentionPolicy.LIMITS

    def __init__(self, subscription_name: str):
        self.name = subscription_name
        self.subjects = [
            f"{self.name}.main",
            f"{self.name}.prefill",
        ]

    @property
    def message_subject(self) -> str:
        return f"{self.name}.main"


class PrefillConsumerQueue(ConsumerQueue):
    """
    Writer: prefill
    Reader: provisioning consumers via the Provisioning API
    """

    @property
    def message_subject(self) -> str:
        return f"{self.name}.prefill"


class LdapQueue(BaseQueue):
    """
    Writer: provisioning-listener module
    Reader: udm-transformer
    """

    name = "ldap-producer"


class IncomingQueue(BaseQueue):
    """
    Writer: udm-transformer
    Reader: dispatcher
    """

    def __init__(self, consumer_name: str):
        self.name = "incoming"
        self._consumer_name = consumer_name

        # In UCS, the retention policy for the incoming queue must be set to INTEREST
        # because multiple dispatchers (master and backups) can connect to the same
        # NATS instance.
        #
        # This is a temporary workaround until an upgrade path is implemented in N4K
        # to migrate the incoming queue from WORK_QUEUE to INTEREST.
        # Once that migration is available, the retention_policy = RetentionPolicy.INTEREST
        # can be defined at the class level.
        # https://git.knut.univention.de/univention/dev/projects/provisioning/-/issues/96#note_563273
        if os.getenv("PLATFORM_UCS", "").lower() == "true":
            self.retention_policy = RetentionPolicy.INTEREST
            self.deliver_policy = DeliverPolicy.NEW


class PrefillQueue(BaseQueue):
    """
    Writer: Provisioning API
    Reader: prefill
    """

    name = "prefill"


class PrefillFailuresQueue(BaseQueue):
    """
    Writer: prefill
    Reader: manual intervention/debugging
    """

    name = "prefill-failures"


class NatsMessageQueue(MessageQueue):
    """
    Message queueing using NATS.

    Use as an asynchronous context manager to ensure the connection gets closed after usage.
    """

    def __init__(self, server: str, user: str, password: str, max_reconnect_attempts: int = 5, **connect_kwargs):
        super().__init__(
            server=server, user=user, password=password, max_reconnect_attempts=max_reconnect_attempts, **connect_kwargs
        )
        self._nats = NATS()
        self._js = self._nats.jetstream()
        self.pull_subscription = None

    async def __aenter__(self) -> Self:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.close()
        return False

    async def connect(self):
        """
        Connect to the NATS server.

        Arguments are passed directly to the NATS client.
        https://nats-io.github.io/nats.py/modules.html#asyncio-client

        By default, it fails after a maximum of 10 seconds because of a 2 second connect timout * 5 reconnect attempts.
        """
        await self._nats.connect(
            servers=self._server,
            user=self._user,
            password=self._password,
            max_reconnect_attempts=self._max_reconnect_attempts,
            error_cb=self.error_callback,
            disconnected_cb=self.disconnected_callback,
            closed_cb=self.closed_callback,
            reconnected_cb=self.reconnected_callback,
            **self._connect_kwargs,
        )

    async def error_callback(self, e):
        logger.error("There was an error during the execution: %s", e)

    async def disconnected_callback(self):
        logger.debug("Disconnected to NATS")

    async def closed_callback(self):
        logger.debug("Closed connection to NATS.")

    async def reconnected_callback(self):
        logger.debug("Reconnected to NATS")

    async def close(self):
        await self._nats.close()

    async def add_message(
        self,
        queue: BaseQueue,
        message: BaseMessage,
        binary_encoder: Callable[[Any], bytes] = json_encoder,
    ):
        """Publish a message to a NATS subject."""

        await self._js.publish(
            subject=queue.message_subject,
            payload=binary_encoder(message.model_dump()),
            stream=queue.queue_name,
        )
        logger.debug(
            "Message was published to the stream: %r with the subject: %r",
            queue.queue_name,
            queue.message_subject,
        )

    async def initialize_subscription(self, queue: BaseQueue) -> None:
        """Initializes a stream for a pull consumer, pull consumers can't define a deliver subject"""
        await self.ensure_stream(queue)
        await self.ensure_consumer(queue)

        self.pull_subscription = await self._js.pull_subscribe(
            subject=queue.message_subject,
            durable=queue.consumer_name,
            stream=queue.queue_name,
        )

    async def get_message(self, queue: BaseQueue, timeout: float, pop: bool) -> Optional[ProvisioningMessage]:
        """Retrieve messages from a NATS subject."""

        try:
            await self._js.stream_info(queue.queue_name)
        except NotFoundError:
            logger.error("The stream '%s' was not found in NATS", queue.queue_name)
            raise

        try:
            consumer = await self._js.consumer_info(queue.queue_name, queue.consumer_name)
        except NotFoundError:
            logger.error("The consumer '%s' was not found in NATS", queue.consumer_name)
            raise

        # TODO: Why is ConsumerInfo passed in as ConsumerConfig?
        sub = await self._js.pull_subscribe(
            queue.message_subject, durable=queue.consumer_name, stream=queue.queue_name, config=consumer
        )
        try:
            msgs = await sub.fetch(1, timeout)
        except asyncio.TimeoutError:
            return None

        if pop:
            await msgs[0].ack()

        return self.provisioning_message_from(msgs[0])

    async def get_one_message(
        self,
        timeout: float = 10,
        binary_decoder: Callable[[bytes], Any] = json_decoder,
    ) -> Tuple[MQMessage, Acknowledgements]:
        """Returns Optionals of Message and a Callable that acknowledges the message."""
        if not self.pull_subscription:
            raise ValueError(
                "Subscription class attribute is empty, ensure that initialize_subscription() has been called."
            )

        try:
            messages = await self.pull_subscription.fetch(1, timeout=timeout)
        except asyncio.TimeoutError:
            raise Empty()

        acknowledgements = self.build_acknowledgements(messages[0])

        return (
            self.mq_message_from(messages[0], binary_decoder=binary_decoder),
            acknowledgements,
        )

    @staticmethod
    def provisioning_message_from(msg: Msg) -> ProvisioningMessage:
        data = json.loads(msg.data)
        sequence_number = int(msg.reply.split(".")[-4])
        message = ProvisioningMessage(
            sequence_number=sequence_number,
            num_delivered=msg.metadata.num_delivered,
            publisher_name=data["publisher_name"],
            ts=data["ts"],
            realm=data["realm"],
            topic=data["topic"],
            body=data["body"],
        )
        return message

    def nats_message_from(self, message: MQMessage) -> Msg:
        data = message.data
        msg = Msg(
            _client=self._nats,
            subject=message.subject,
            reply=message.reply,
            data=json.dumps(data).encode("utf-8"),
            headers=message.headers,
        )
        return msg

    @staticmethod
    def mq_message_from(msg: Msg, binary_decoder: Callable[[bytes], Any] = json_decoder) -> MQMessage:
        data = binary_decoder(msg.data)
        sequence_number = int(msg.reply.split(".")[-4])
        message = MQMessage(
            subject=msg.subject,
            reply=msg.reply,
            data=data,
            headers=msg.headers,
            num_delivered=msg.metadata.num_delivered,
            sequence_number=sequence_number,
        )
        return message

    async def delete_stream(self, queue: BaseQueue):
        """Delete the entire stream for a given name in NATS JetStream."""
        try:
            await self._js.delete_stream(queue.queue_name)
        except NotFoundError:
            return None

    async def delete_consumer(self, queue: BaseQueue):
        try:
            await self._js.delete_consumer(queue.queue_name, queue.consumer_name)
        except NotFoundError:
            return None

    async def stream_exists(self, queue: BaseQueue) -> bool:
        try:
            await self._js.stream_info(queue.queue_name)
        except NotFoundError:
            return False
        return True

    async def ensure_stream(self, queue: BaseQueue):
        try:
            await self._js.stream_info(queue.queue_name)
            logger.info("A stream with the name %r already exists", queue.queue_name)
        except NotFoundError:
            await self._js.add_stream(queue.stream_config())
            logger.info("A stream with the name %r was created", queue.queue_name)
        else:
            await self._js.update_stream(queue.stream_config())
            logger.info("A stream with the name %r was updated", queue.queue_name)

    async def ensure_consumer(self, queue: BaseQueue):
        try:
            await self._js.consumer_info(queue.queue_name, queue.consumer_name)
            logger.info("A consumer with the name %r already exists", queue.consumer_name)
        except NotFoundError:
            await self._js.add_consumer(
                queue.queue_name,
                queue.consumer_config(),
            )
            logger.info("A consumer with the name %r was created", queue.consumer_name)

    def build_acknowledgements(self, message: Msg) -> Acknowledgements:
        return Acknowledgements(
            message.ack,
            message.nak,
            message.in_progress,
        )

    async def acknowledge_message(self, message: MQMessage):
        msg = self.nats_message_from(message)
        await msg.ack()

    async def acknowledge_message_negatively(self, message: MQMessage):
        msg = self.nats_message_from(message)
        await msg.nak()

    async def acknowledge_message_in_progress(self, message: MQMessage):
        msg = self.nats_message_from(message)
        await msg.in_progress()

    async def delete_message(self, queue: BaseQueue, seq_num: int):
        logger.info("Deleting message from the stream: %r", queue.queue_name)
        try:
            await self._js.get_msg(queue.queue_name, seq_num)
            await self._js.delete_msg(queue.queue_name, seq_num)
            logger.info("Message was deleted")
        except (ServerError, NotFoundError) as exc:
            raise ValueError(exc.description)

    async def purge_stream(self, queue: BaseQueue) -> None:
        await self._js.purge_stream(queue.queue_name, subject=queue.message_subject)
