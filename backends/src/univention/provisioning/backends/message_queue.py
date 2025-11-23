# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Coroutine, NamedTuple

from pydantic import BaseModel
from typing_extensions import Self

logger = logging.getLogger(__name__)


class MQMessage(BaseModel):
    """Raw message queue message."""

    subject: str
    reply: str
    data: dict[str, Any]
    num_delivered: int
    sequence_number: int
    headers: dict[str, str] | None = None


class Empty(Exception): ...


class QueueStatus(Enum):
    """Status returned by queue initialization and migration operations."""

    READY = "ready"
    SEALED_FOR_MIGRATION = "sealed_for_migration"


def json_encoder(data: Any) -> bytes:
    return json.dumps(data).encode("utf-8")


def json_decoder(data: Any) -> bytes:
    return json.loads(data)


class Acknowledgements(NamedTuple):
    acknowledge_message: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_negatively: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]]


class MessageQueue(ABC):
    """
    The base class for message queueing.

    Use as an asynchronous context manager to ensure the connection gets closed after usage.
    """

    def __init__(self, server: str, user: str, password: str, max_reconnect_attempts: int = 5, **connect_kwargs):
        self._server = server
        self._user = user
        self._password = password
        self._max_reconnect_attempts = max_reconnect_attempts
        self._connect_kwargs = connect_kwargs

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool: ...

    @abstractmethod
    async def connect(self):
        """
        Connect to the NATS server.

        Arguments are passed directly to the NATS client.
        https://nats-io.github.io/nats.py/modules.html#asyncio-client

        By default, it fails after a maximum of 10 seconds because of a 2 second connect timout * 5 reconnect attempts.
        """
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def add_message(
        self,
        queue,
        message: bytes,
    ):
        """Publish a message to a NATS subject."""
        pass

    @abstractmethod
    async def initialize_subscription(self, queue, migrate_stream: bool = False) -> QueueStatus:
        """Initialize a subscription to a queue.

        Args:
            queue: The queue configuration
            migrate_stream: If True, migrate stream when configuration differs

        Returns:
            QueueStatus
        """
        pass

    @abstractmethod
    async def get_message(self, queue, timeout: float, pop: bool):
        """Retrieve multiple messages from a NATS subject."""
        pass

    @abstractmethod
    async def get_one_message(
        self,
        timeout: float = 10,
        binary_decoder: Callable[[bytes], Any] = json_decoder,
    ) -> tuple[MQMessage, Acknowledgements]:
        pass

    @abstractmethod
    async def delete_message(self, queue, seq_num: int):
        pass

    @abstractmethod
    async def delete_stream(self, queue):
        pass

    @abstractmethod
    async def acknowledge_message(self, message: MQMessage):
        pass

    @abstractmethod
    async def acknowledge_message_negatively(self, message: MQMessage):
        pass

    @abstractmethod
    async def acknowledge_message_in_progress(self, message: MQMessage):
        pass

    @abstractmethod
    async def delete_consumer(self, queue):
        pass

    @abstractmethod
    async def stream_exists(self, queue):
        pass

    @abstractmethod
    async def ensure_stream(self, queue):
        pass

    @abstractmethod
    async def ensure_consumer(self, queue):
        pass

    @abstractmethod
    async def purge_stream(self, queue) -> None:
        pass


class MessageAckManager:
    def __init__(self, ack_wait: int = 30, ack_threshold: int = 5):
        self.ack_wait = ack_wait
        self.ack_threshold = ack_threshold

    async def process_message_with_ack_wait_extension(
        self,
        message_handler: Coroutine[Any, Any, None],
        acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Combines message processing and automatic AckWait extension.
        """

        async with asyncio.TaskGroup() as task_group:
            ack_extender = task_group.create_task(self.extend_ack_wait(acknowledge_message_in_progress))
            message_handler_task = task_group.create_task(message_handler)

            await message_handler_task
            ack_extender.cancel()

    async def extend_ack_wait(self, acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]]) -> None:
        while True:
            await asyncio.sleep(self.ack_wait - self.ack_threshold)
            await acknowledge_message_in_progress()
            logger.info("AckWait was extended")
