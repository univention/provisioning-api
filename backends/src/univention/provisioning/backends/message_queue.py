# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine, List, NamedTuple, Optional, Tuple

from nats.aio.msg import Msg

from univention.provisioning.models.message import BaseMessage, MQMessage


def json_encoder(data: Any) -> bytes:
    return json.dumps(data).encode("utf-8")


def json_decoder(data: Any) -> bytes:
    return json.loads(data)


class Acknowledgements(NamedTuple):
    acknowledge_message: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_negatively: Callable[[], Coroutine[Any, Any, None]]
    acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]]


class MessageQueue(ABC):
    """The base class for message queueing."""

    def __init__(self, server: str, user: str, password: str, max_reconnect_attempts: int = 5, **connect_kwargs):
        self._server = server
        self._user = user
        self._password = password
        self._max_reconnect_attempts = max_reconnect_attempts
        self._connect_kwargs = connect_kwargs

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
        stream: str,
        subject: str,
        message: BaseMessage,
        binary_encoder: Callable[[Any], bytes] = json_encoder,
    ):
        """Publish a message to a NATS subject."""
        pass

    @abstractmethod
    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: Optional[str]) -> None:
        pass

    @abstractmethod
    async def get_message(self, stream: str, subject: str, timeout: float, pop: bool):
        """Retrieve multiple messages from a NATS subject."""
        pass

    @abstractmethod
    async def get_one_message(
        self,
        timeout: float = 10,
        binary_decoder: Callable[[bytes], Any] = json_decoder,
    ) -> Tuple[MQMessage, Acknowledgements]:
        pass

    @abstractmethod
    async def delete_message(self, stream: str, seq_num: int):
        pass

    @abstractmethod
    async def delete_stream(self, stream_name: str):
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
    async def delete_consumer(self, subject: str):
        pass

    @abstractmethod
    async def cb(self, msg):
        pass

    @abstractmethod
    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        pass

    @abstractmethod
    async def wait_for_event(self) -> Msg:
        pass

    @abstractmethod
    async def stream_exists(self, subject: str):
        pass

    @abstractmethod
    async def ensure_stream(self, stream: str, manual_delete: bool, subjects: Optional[List[str]] = None):
        pass

    @abstractmethod
    async def ensure_consumer(self, subject: str, deliver_subject: Optional[str] = None):
        pass
