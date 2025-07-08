# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import abc
from typing import Self

from univention.provisioning.backends_core.message import MQMessage
from univention.provisioning.backends_core.message_queue import Acknowledgements
from univention.provisioning.models.message import BaseMessage

from .config import PrefillSettings


class MessageQueuePort(abc.ABC):
    """
    Handle a message queue communication.

    Use as an async context manager.
    """

    @abc.abstractmethod
    def __init__(self, settings: PrefillSettings | None = None): ...

    @abc.abstractmethod
    async def __aenter__(self) -> Self: ...

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool: ...

    @abc.abstractmethod
    async def add_message_to_failures_queue(self, message: BaseMessage) -> None: ...

    @abc.abstractmethod
    async def add_message_to_queue(self, queue: str, message: BaseMessage) -> None: ...

    @abc.abstractmethod
    async def get_one_message(self) -> tuple[MQMessage, Acknowledgements]: ...

    @abc.abstractmethod
    async def initialize_subscription(self) -> None: ...

    @abc.abstractmethod
    async def prepare_failures_queue(self) -> None: ...

    @abc.abstractmethod
    async def purge_queue(self, name: str) -> None: ...
