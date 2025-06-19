# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import json
import logging
from typing import Any, Callable, List, Optional, Tuple

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig, RetentionPolicy, StreamConfig
from nats.js.errors import NotFoundError, ServerError
from typing_extensions import Self

from univention.provisioning.models.message import BaseMessage, MQMessage, ProvisioningMessage

from .message_queue import Acknowledgements, Empty, MessageQueue, json_decoder, json_encoder

logger = logging.getLogger(__name__)


class NatsKeys:
    """A list of keys used in Nats for queueing messages."""

    @staticmethod
    def stream(subject: str) -> str:
        return f"stream:{subject}"

    @staticmethod
    def durable_name(subject: str) -> str:
        return f"durable_name:{subject}"


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
        self._message_queue = asyncio.Queue()
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
        stream: str,
        subject: str,
        message: BaseMessage,
        binary_encoder: Callable[[Any], bytes] = json_encoder,
    ):
        """Publish a message to a NATS subject."""
        stream_name = NatsKeys.stream(stream)

        await self._js.publish(
            subject,
            binary_encoder(message.model_dump()),
            stream=stream_name,
        )
        logger.debug(
            "Message was published to the stream: %r with the subject: %r",
            stream_name,
            subject,
        )

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: Optional[str]) -> None:
        """Initializes a stream for a pull consumer, pull consumers can't define a deliver subject"""
        await self.ensure_stream(stream, manual_delete, [subject] if subject else None)
        await self.ensure_consumer(stream)

        durable_name = NatsKeys.durable_name(stream)
        stream_name = NatsKeys.stream(stream)
        self.pull_subscription = await self._js.pull_subscribe(
            subject=subject if subject else "*",
            durable=durable_name,
            stream=stream_name,
            config=ConsumerConfig(
                num_replicas=1
            ),  # NOTE: this needs to be configurable in the future  https://docs.nats.io/nats-concepts/jetstream
        )

    async def get_message(self, stream: str, subject: str, timeout: float, pop: bool) -> Optional[ProvisioningMessage]:
        """Retrieve multiple messages from a NATS subject."""

        stream_name = NatsKeys.stream(stream)
        # TODO: Why the stream and not the subject?
        durable_name = NatsKeys.durable_name(stream)

        try:
            await self._js.stream_info(stream_name)
        except NotFoundError:
            logger.error("The stream '%s' was not found in NATS", stream_name)
            raise

        try:
            consumer = await self._js.consumer_info(stream_name, durable_name)
        except NotFoundError:
            logger.error("The consumer '%s' was not found in NATS", durable_name)
            raise

        # TODO: Why is ConsumerInfo passed in as ConsumerConfig?
        sub = await self._js.pull_subscribe(subject, durable=durable_name, stream=stream_name, config=consumer)
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

    async def delete_stream(self, stream_name: str):
        """Delete the entire stream for a given name in NATS JetStream."""
        try:
            await self._js.delete_stream(NatsKeys.stream(stream_name))
        except NotFoundError:
            return None

    async def delete_consumer(self, subject: str):
        try:
            await self._js.delete_consumer(NatsKeys.stream(subject), NatsKeys.durable_name(subject))
        except NotFoundError:
            return None

    async def cb(self, msg):
        await self._message_queue.put(msg)

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.ensure_stream(subject, False)
        await self.ensure_consumer(subject, deliver_subject)

        await self._js.subscribe(
            subject,
            cb=self.cb,
            durable=NatsKeys.durable_name(subject),
            stream=NatsKeys.stream(subject),
            manual_ack=True,
        )

    async def wait_for_event(self) -> MQMessage:
        msg = await self._message_queue.get()
        message = self.mq_message_from(msg)
        return message

    async def stream_exists(self, subject: str) -> bool:
        try:
            await self._js.stream_info(NatsKeys.stream(subject))
        except NotFoundError:
            return False
        return True

    async def ensure_stream(self, stream: str, manual_delete: bool, subjects: Optional[List[str]] = None):
        stream_name = NatsKeys.stream(stream)
        stream_config = StreamConfig(
            name=stream_name,
            subjects=subjects or [stream],
            retention=RetentionPolicy.LIMITS if manual_delete else RetentionPolicy.WORK_QUEUE,
            # TODO: set to 3 after nats clustering is stable.
            num_replicas=1,
        )
        try:
            await self._js.stream_info(stream_name)
            logger.info("A stream with the name %r already exists", stream_name)
        except NotFoundError:
            await self._js.add_stream(stream_config)
            logger.info("A stream with the name %r was created", stream_name)
        else:
            await self._js.update_stream(stream_config)
            logger.info("A stream with the name %r was updated", stream_name)

    async def ensure_consumer(self, stream: str, deliver_subject: Optional[str] = None):
        stream_name = NatsKeys.stream(stream)
        durable_name = NatsKeys.durable_name(stream)

        try:
            await self._js.consumer_info(stream_name, durable_name)
            logger.info("A consumer with the name %r already exists", durable_name)
        except NotFoundError:
            await self._js.add_consumer(
                stream_name,
                ConsumerConfig(
                    durable_name=durable_name,
                    deliver_subject=deliver_subject,
                    max_ack_pending=1,
                ),
            )
            logger.info("A consumer with the name %r was created", durable_name)

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

    async def delete_message(self, stream: str, seq_num: int):
        logger.info("Deleting message from the stream: %r", stream)
        try:
            await self._js.get_msg(NatsKeys.stream(stream), seq_num)
            await self._js.delete_msg(NatsKeys.stream(stream), seq_num)
            logger.info("Message was deleted")
        except (ServerError, NotFoundError) as exc:
            raise ValueError(exc.description)

    async def purge_stream(self, stream: str, subject: str) -> None:
        await self._js.purge_stream(NatsKeys.stream(stream), subject=subject)
