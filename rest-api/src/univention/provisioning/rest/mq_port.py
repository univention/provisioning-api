# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import abc
from typing import Optional, Self

from univention.provisioning.backends.nats_mq import BaseQueue
from univention.provisioning.models.message import Message, ProvisioningMessage
from univention.provisioning.models.subscription import NewSubscription

from .config import AppSettings


class MessageQueuePort(abc.ABC):
    """
    Handle a message queue communication.

    Use as an async context manager.
    """

    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings

    @abc.abstractmethod
    async def __aenter__(self) -> Self: ...

    @abc.abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool: ...

    @abc.abstractmethod
    async def add_message(self, queue: BaseQueue, message: Message) -> None: ...

    @abc.abstractmethod
    async def get_message(self, queue: BaseQueue, timeout: float, pop: bool) -> Optional[ProvisioningMessage]: ...

    @abc.abstractmethod
    async def delete_message(self, queue: BaseQueue, seq_num: int): ...

    @abc.abstractmethod
    async def create_queue(self, queue: BaseQueue): ...

    @abc.abstractmethod
    async def delete_queue(self, queue: BaseQueue): ...

    @abc.abstractmethod
    async def create_consumer(self, queue: BaseQueue): ...

    @abc.abstractmethod
    async def delete_consumer(self, queue: BaseQueue): ...

    @abc.abstractmethod
    async def request_prefill(self, subscription: NewSubscription): ...
