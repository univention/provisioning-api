# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import logging
from typing import Any, Callable

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig, RetentionPolicy, StreamConfig
from nats.js.errors import NotFoundError

from .message import MQMessage
from .message_queue import Acknowledgements, Empty, NatsMessageQueueSettings, json_decoder

logger = logging.getLogger(__name__)


def stream_builder(subject: str) -> str:
    return f"stream:{subject}"


def durable_name_builder(subject: str) -> str:
    return f"durable_name:{subject}"


class NatsMessageQueue:
    """
    Message queueing using NATS.
    """

    def __init__(self, settings: NatsMessageQueueSettings, **connect_kwargs):
        self.settings = settings
        self._connect_kwargs = connect_kwargs

        self._nats = NATS()
        self._js = self._nats.jetstream()

    async def connect(self):
        """
        Connect to the NATS server.

        Arguments are passed directly to the NATS client.
        https://nats-io.github.io/nats.py/modules.html#asyncio-client

        By default, it fails after a maximum of 10 seconds because of a 2 second connect timout * 5 reconnect attempts.
        """
        await self._nats.connect(
            servers=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
            error_cb=self.error_callback,
            disconnected_cb=self.disconnected_callback,
            closed_cb=self.closed_callback,
            reconnected_cb=self.reconnected_callback,
            **self._connect_kwargs,
        )

    async def error_callback(self, e):
        logger.error("There was an error during the execution: %s", e)
        raise (e)

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
        payload: bytes,
    ):
        """Publish a message to a NATS subject."""
        stream_name = stream_builder(stream)
        await self._js.publish(
            subject,
            payload,
            stream=stream_name,
        )
        logger.debug(
            "Message was published to the stream: %r with the subject: %r",
            stream_name,
            subject,
        )

    async def ensure_stream(self, stream: str, manual_delete: bool, subjects: list[str] | None = None):
        stream_name = stream_builder(stream)
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

    async def ensure_consumer(self, stream: str, deliver_subject: str | None = None):
        stream_name = stream_builder(stream)
        durable_name = durable_name_builder(stream)

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

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str | None) -> None:
        """Initializes a stream for a pull consumer, pull consumers can't define a deliver subject"""
        await self.ensure_stream(stream, manual_delete, [subject] if subject else None)
        await self.ensure_consumer(stream)

        durable_name = durable_name_builder(stream)
        stream_name = stream_builder(stream)
        self.pull_subscription = await self._js.pull_subscribe(
            subject=subject if subject else "*",
            durable=durable_name,
            stream=stream_name,
            config=ConsumerConfig(
                num_replicas=self.settings.nats_message_replicas,
            ),
        )

    async def get_one_message(
        self,
        timeout: float = 10,
        binary_decoder: Callable[[bytes], Any] = json_decoder,
    ) -> tuple[MQMessage, Acknowledgements]:
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

    def build_acknowledgements(self, message: Msg) -> Acknowledgements:
        return Acknowledgements(
            message.ack,
            message.nak,
            message.in_progress,
        )

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

    async def purge_stream(self, stream: str, subject: str) -> None:
        await self._js.purge_stream(stream_builder(stream), subject=subject)
