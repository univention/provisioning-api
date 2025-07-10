# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import json
import logging
from abc import abstractmethod
from typing import Any, Callable, Coroutine, NamedTuple, Protocol, runtime_checkable

from .message import MQMessage

logger = logging.getLogger(__file__)


class Empty(Exception): ...


def json_decoder(data: Any) -> bytes:
    return json.loads(data)


class NatsMessageQueueSettings(Protocol):
    # Nats user name specific to UdmProducerSettings
    nats_user: str
    # Nats password specific to UdmProducerSettings
    nats_password: str
    # Maximum number of reconnect attempts to the NATS server
    nats_max_reconnect_attempts: int
    # Nats message replication amount. Useful values are 1, 3 and 5
    nats_message_replicas: int

    @property
    @abstractmethod
    def nats_server(self) -> str: ...


class Acknowledgements(NamedTuple):
    acknowledge_message: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_negatively: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]]


@runtime_checkable
class MessageQueuePort(Protocol):
    """
    Abstract port for an asynchronous message queue.
    """

    async def connect(self) -> None: ...

    async def close(self) -> None: ...

    async def add_message(
        self,
        stream: str,
        subject: str,
        payload: bytes,
    ) -> None: ...

    async def ensure_stream(
        self,
        stream: str,
        manual_delete: bool,
        subjects: list[str] | None = None,
    ) -> None: ...

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str | None) -> None: ...

    async def get_one_message(
        self,
        timeout: float = 10,
        binary_decoder: Callable[[bytes], Any] = json_decoder,
    ) -> tuple[MQMessage, Acknowledgements]: ...

    async def get_message(self, stream: str, subject: str, timeout: float, pop: bool) -> MQMessage | None: ...


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
