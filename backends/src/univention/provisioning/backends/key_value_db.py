# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from abc import ABC, abstractmethod
from enum import Enum
from typing import AsyncGenerator, Awaitable, Callable, List, Optional, Tuple, Union

from univention.provisioning.models.subscription import Subscription


class BucketName(str, Enum):
    subscriptions = "SUBSCRIPTIONS"
    credentials = "CREDENTIALS"
    cache = "CACHE"


class UpdateConflict(Exception): ...


class KeyValueDB(ABC):
    """The base class for key-value store adapters."""

    def __init__(self, server: str, user: str, password: str):
        self._server = server
        self._user = user
        self._password = password

    @abstractmethod
    async def init(self, buckets: List[BucketName]):
        pass

    @abstractmethod
    async def close(self):
        pass

    @abstractmethod
    async def create_kv_store(self, bucket: BucketName):
        pass

    @abstractmethod
    async def delete_kv_pair(self, key: str, bucket: BucketName):
        pass

    @abstractmethod
    async def get_value(self, key: str, bucket: BucketName) -> Optional[str]:
        """
        Retrieve value at `key` in `bucket`.
        Returns the value or None if key does not exist.
        """
        pass

    @abstractmethod
    async def get_value_with_revision(self, key: str, bucket: BucketName) -> Optional[Tuple[str, int]]:
        """
        Retrieve value and latest version (revision) at `key` in `bucket`.
        Returns a tuple (value, revision) or None if key does not exist.
        """
        pass

    @abstractmethod
    async def put_value(
        self, key: str, value: Union[str, dict, list], bucket: BucketName, revision: Optional[int] = None
    ) -> None:
        """
        Store `value` at `key` in `bucket`.
        If `revision` is None overwrite value in DB without a further check.
        If `revision` is not None and the revision in the DB is different, raise UpdateConflict.
        """
        pass

    @abstractmethod
    async def get_keys(self, bucket: BucketName) -> List[str]:
        pass

    @abstractmethod
    async def get_all_subscriptions(self) -> AsyncGenerator[Subscription, None]:
        pass

    @abstractmethod
    async def watch_for_subscription_changes(self, callback: Callable[[str, Optional[bytes]], Awaitable[None]]) -> None:
        """
        Call the `callback` function for any change to the Subscriptions KV bucket.

        :param callback: Async function that accepts two arguments: the key of the changed entry (str)
            and its value (bytes). When the value is None, the key has been deleted.
        """
        pass
