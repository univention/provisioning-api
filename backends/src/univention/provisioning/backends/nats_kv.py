# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
from typing import Any, AsyncGenerator, Awaitable, Callable, List, Optional, Tuple, Union

from nats.aio.client import Client as NATS
from nats.js.errors import BucketNotFoundError, KeyNotFoundError, KeyWrongLastSequenceError, NoKeysError
from nats.js.kv import KV_DEL, KV_PURGE

from .key_value_db import BucketName, KeyValueDB, UpdateConflict

logger = logging.getLogger(__name__)


class NatsKeyValueDB(KeyValueDB):
    """A key-value store using NATS as backend."""

    def __init__(self, server: str, user: str, password: str):
        super().__init__(server=server, user=user, password=password)
        self._nats = NATS()
        self._js = self._nats.jetstream()

    async def init(self, buckets: List[BucketName]):
        await self._nats.connect(
            servers=self._server,
            user=self._user,
            password=self._password,
            max_reconnect_attempts=1,
        )
        for bucket in buckets:
            await self.create_kv_store(bucket)

    async def close(self):
        await self._nats.close()

    # TODO: Rename to ensure_kv_store()
    async def create_kv_store(self, bucket: BucketName):
        try:
            await self._js.key_value(bucket.value)
        except BucketNotFoundError:
            logger.info("Creating bucket with the name: %r", bucket)
            await self._js.create_key_value(bucket=bucket.value)

    async def delete_kv_pair(self, key: str, bucket: BucketName):
        kv_store = await self._js.key_value(bucket.value)
        await kv_store.delete(key)

    async def get_value(self, key: str, bucket: BucketName) -> Optional[str]:
        """
        Retrieve value at `key` in `bucket`.
        Returns the value or None if key does not exist.
        """
        result = await self.get_value_with_revision(key, bucket)
        return result[0] if result else None

    async def get_value_with_revision(self, key: str, bucket: BucketName) -> Optional[Tuple[str, int]]:
        """
        Retrieve value and latest version (revision) at `key` in `bucket`.
        Returns a tuple (value, revision) or None if key does not exist.
        """
        kv_store = await self._js.key_value(bucket.value)
        try:
            result = await kv_store.get(key)
            return result.value.decode("utf-8"), result.revision if result else None
        except KeyNotFoundError:
            pass

    async def put_value(
        self, key: str, value: Union[str, dict, list], bucket: BucketName, revision: Optional[int] = None
    ) -> None:
        """
        Store `value` at `key` in `bucket`.
        If `revision` is None overwrite value in DB without a further check.
        If `revision` is not None and the revision in the DB is different, raise UpdateConflict.
        """
        kv_store = await self._js.key_value(bucket.value)

        if not value:
            # Avoid creating a pair with an empty value
            await self.delete_kv_pair(key, bucket)
            return

        if not isinstance(value, str):
            value = json.dumps(value)

        if revision:
            try:
                await kv_store.update(key, value.encode("utf-8"), revision)
            except KeyWrongLastSequenceError as exc:
                raise UpdateConflict(str(exc)) from exc
        else:
            await kv_store.put(key, value.encode("utf-8"))
            return

    async def get_keys(self, bucket: BucketName) -> List[str]:
        kv_store = await self._js.key_value(bucket.value)
        try:
            return await kv_store.keys()
        except NoKeysError:
            return []

    async def get_all_bucket_items(self, bucket: str) -> AsyncGenerator[dict[str, Any], None]:
        kv_store = await self._js.key_value(bucket)
        for key in await self.get_keys(BucketName(bucket)):
            entry = await kv_store.get(key)
            item_dict = json.loads(entry.value)
            yield item_dict

    async def watch_for_subscription_changes(self, callback: Callable[[str, Optional[bytes]], Awaitable[None]]) -> None:
        """
        Call the `callback` function for any change to the Subscriptions KV bucket.

        :param callback: Async function that accepts two arguments: the key of the changed entry (str)
            and its value (bytes). When the value is None, the key has been deleted.
        """
        kv_store = await self._js.key_value(BucketName.subscriptions.value)
        watcher = await kv_store.watchall()

        while True:
            logger.debug("Waiting for subscription changes...")
            async for update in watcher:
                # update is of type: nats.js.kv.KeyValue.Entry
                # update.key is the subscription's name
                # update.values is the JSON dump of a Subscription object or None when the key was deleted/purged
                # update.operation is the type of operation that triggered this
                if not update:
                    continue
                try:
                    await callback(update.key, None if update.operation in {KV_DEL, KV_PURGE} else update.value)
                except Exception as e:
                    logger.error("Error occurred while processing subscription change. key=%r exc=%s", update.key, e)
