# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from abc import abstractmethod
from typing import Protocol

from nats.aio.client import Client as NATS
from nats.js.api import RetentionPolicy, StreamConfig
from nats.js.errors import NotFoundError

logger = logging.getLogger(__name__)


class NatsMessageQueueSettings(Protocol):
    # Nats user name specific to UdmProducerSettings
    nats_user: str
    # Nats password specific to UdmProducerSettings
    nats_password: str
    # Maximum number of reconnect attempts to the NATS server
    nats_max_reconnect_attempts: int

    @property
    @abstractmethod
    def nats_server(self) -> str: ...


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
        self.js = self._nats.jetstream()

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
        await self.js.publish(
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
            await self.js.stream_info(stream_name)
            logger.info("A stream with the name %r already exists", stream_name)
        except NotFoundError:
            await self.js.add_stream(stream_config)
            logger.info("A stream with the name %r was created", stream_name)
        else:
            await self.js.update_stream(stream_config)
            logger.info("A stream with the name %r was updated", stream_name)
