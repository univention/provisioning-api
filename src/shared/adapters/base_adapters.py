# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from abc import ABC, abstractmethod
from typing import Union, Optional

from nats.aio.msg import Msg
from nats.js.kv import KeyValue

from shared.models import Message
from shared.models.queue import MQMessage


class BaseKVStoreAdapter(ABC):
    """The base class for key-value store adapters."""

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def create_kv_store(self, name: str = "Pub_Sub_KV"):
        pass

    @abstractmethod
    async def delete_kv_pair(self, key: str):
        pass

    @abstractmethod
    async def get_value(self, key: str) -> Optional[KeyValue.Entry]:
        pass

    @abstractmethod
    async def put_value(self, key: str, value: Union[str, dict]):
        pass


class BaseMQAdapter(ABC):
    """The base class for message queue adapters."""

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def add_message(self, subject: str, message: Message):
        pass

    @abstractmethod
    async def get_messages(self, subject: str, timeout: float, count: int, pop: bool):
        pass

    @abstractmethod
    async def remove_message(self, msg: Union[Msg, MQMessage]):
        pass

    @abstractmethod
    async def delete_stream(self, stream_name: str):
        pass

    @abstractmethod
    async def cb(self, msg):
        pass

    @abstractmethod
    async def subscribe_to_queue(self, subject):
        pass

    @abstractmethod
    async def wait_for_event(self) -> Msg:
        pass
