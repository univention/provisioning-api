# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from abc import ABC, abstractmethod
from typing import Any, Callable, List, Optional, Tuple, Union

from nats.aio.msg import Msg

from univention.provisioning.models import BaseMessage
from univention.provisioning.models.subscription import Bucket


class BaseKVStoreAdapter(ABC):
    """The base class for key-value store adapters."""

    @abstractmethod
    async def init(self, server: str, user: str, password: str, buckets: List[Bucket]):
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
    async def get_value(self, key: str, bucket: Bucket) -> Optional[str]:
        """
        Retrieve value at `key` in `bucket`.
        Returns the value or None if key does not exist.
        """
        pass

    @abstractmethod
    async def get_value_with_revision(self, key: str, bucket: Bucket) -> Optional[Tuple[str, int]]:
        """
        Retrieve value and latest version (revision) at `key` in `bucket`.
        Returns a tuple (value, revision) or None if key does not exist.
        """
        pass

    @abstractmethod
    async def put_value(
        self, key: str, value: Union[str, dict, list], bucket: Bucket, revision: Optional[int] = None
    ) -> None:
        """
        Store `value` at `key` in `bucket`.
        If `revision` is None overwrite value in DB without a further check.
        If `revision` is not None and the revision in the DB is different, raise UpdateConflict.
        """
        pass


class BaseMQAdapter(ABC):
    """The base class for message queue adapters."""

    @abstractmethod
    async def connect(self, server: str, user: str, password: str):
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
        binary_encoder: Callable[[Any], bytes],
    ):
        pass

    async def get_message(self, stream: str, subject: str, timeout: float, pop: bool):
        pass

    @abstractmethod
    async def delete_message(self, stream: str, seq_num: int):
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
    async def ensure_stream(self, subject: str):
        pass

    @abstractmethod
    async def ensure_consumer(self, subject: str, deliver_subject: Optional[str] = None):
        pass
