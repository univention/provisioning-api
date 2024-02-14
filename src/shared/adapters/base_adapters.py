# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from abc import ABC, abstractmethod
from typing import Union, Optional, List

from nats.aio.msg import Msg
from nats.js.kv import KeyValue

from shared.models import Message
from shared.models.queue import MQMessage
from shared.models.subscription import Bucket


class BaseKVStoreAdapter(ABC):
    """The base class for key-value store adapters."""

    @abstractmethod
    async def setup_nats_and_kv(self, buckets: List[str]):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def create_kv_store(self, bucket: Bucket):
        pass

    @abstractmethod
    async def delete_kv_pair(self, key: str, bucket: Bucket):
        pass

    @abstractmethod
    async def get_value(self, key: str, bucket: Bucket) -> Optional[KeyValue.Entry]:
        pass

    @abstractmethod
    async def put_value(self, key: str, value: Union[str, dict], bucket: Bucket):
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
    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        pass

    @abstractmethod
    async def wait_for_event(self) -> Msg:
        pass

    @abstractmethod
    async def stream_exists(self, subject: str):
        pass

    @abstractmethod
    async def create_stream(self, subject: str):
        pass

    @abstractmethod
    async def create_consumer(
        self, subject: str, deliver_subject: Optional[str] = None
    ):
        pass
