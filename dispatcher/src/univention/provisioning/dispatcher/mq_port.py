# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import abc
from typing import Optional, Self

from univention.provisioning.backends.message_queue import Acknowledgements
from univention.provisioning.models.message import Message, MQMessage

from .config import DispatcherSettings


class MessageQueuePort(abc.ABC):
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        self.settings = settings

    @abc.abstractmethod
    async def __aenter__(self) -> Self: ...

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool: ...

    @abc.abstractmethod
    async def connect(self) -> None: ...

    @abc.abstractmethod
    async def close(self) -> None: ...

    @abc.abstractmethod
    async def enqueue_message(self, queue: str, message: Message) -> None: ...

    @abc.abstractmethod
    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str) -> None: ...

    @abc.abstractmethod
    async def get_one_message(self, timeout: float) -> tuple[MQMessage, Acknowledgements]: ...

    @abc.abstractmethod
    async def stream_exists(self, stream: str) -> bool: ...
