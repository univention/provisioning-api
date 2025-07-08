# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
from typing import AsyncGenerator, Awaitable, Callable

from nats.aio.client import Client as NATS
from nats.js.errors import (
    BucketNotFoundError,
    KeyNotFoundError,
    KeyWrongLastSequenceError,
    NoKeysError,
)
from nats.js.kv import KV_DEL, KV_PURGE

from univention.provisioning.backends_core.constants import BucketName
from univention.provisioning.backends_core.message_queue import NatsMessageQueueSettings

from .key_value_db import UpdateConflict

logger = logging.getLogger(__name__)


class NatsKeyValueDB:
    """A key-value store using NATS as backend."""

    def __init__(self, settings: NatsMessageQueueSettings, **connect_kwargs):
        self.settings = settings
        self._connect_kwargs = connect_kwargs

        self._nats = NATS()
        self._js = self._nats.jetstream()

    async def init(self, buckets: list[BucketName]):
        await self._nats.connect(
            servers=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
            error_cb=self._error_callback,
            **self._connect_kwargs,
        )
        for bucket in buckets:
            await self._ensure_kv_store(bucket)

    async def _error_callback(self, e):
        logger.error("There was an error during the execution: %s", e)
        raise (e)

    async def close(self):
        await self._nats.close()

    # TODO: Rename to ensure_kv_store()
    async def _ensure_kv_store(self, bucket: BucketName):
        try:
            await self._js.key_value(bucket.value)
        except BucketNotFoundError:
            logger.info("Creating bucket with the name: %r", bucket)
            await self._js.create_key_value(bucket=bucket.value)

    async def _delete_kv_pair(self, key: str, bucket: BucketName):
        kv_store = await self._js.key_value(bucket.value)
        await kv_store.delete(key)

    async def get_value(self, key: str, bucket: BucketName) -> str | None:
        """
        Retrieve value at `key` in `bucket`.
        Returns the value or None if key does not exist.
        """
        result = await self.get_value_with_revision(key, bucket)
        return result[0] if result else None

    async def get_value_with_revision(self, key: str, bucket: BucketName) -> tuple[str, int | None] | None:
        """
        Retrieve value and latest version (revision) at `key` in `bucket`.
        Returns a tuple (value, revision) or None if key does not exist.
        """
        kv_store = await self._js.key_value(bucket.value)
        try:
            result = await kv_store.get(key)
        except KeyNotFoundError:
            return None
        if not result.value:
            return None
        return result.value.decode("utf-8"), result.revision if result else None

    async def put_value(
        self, key: str, value: str | dict | list, bucket: BucketName, revision: int | None = None
    ) -> None:
        """
        Store `value` at `key` in `bucket`.
        If `revision` is None overwrite value in DB without a further check.
        If `revision` is not None and the revision in the DB is different, raise UpdateConflict.
        """
        kv_store = await self._js.key_value(bucket.value)

        if not value:
            # Avoid creating a pair with an empty value
            await self._delete_kv_pair(key, bucket)
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

    async def get_bucket_items(self, bucket_name: BucketName) -> AsyncGenerator[tuple[str, bytes | None], None]:
        kv_store = await self._js.key_value(bucket_name.value)
        try:
            keys = await kv_store.keys()
        except NoKeysError:
            return
        for key in keys:
            entry = await kv_store.get(key)
            yield key, entry.value

    async def watch_for_changes_in_bucket(
        self, bucket_name: BucketName, callback: Callable[[str, bytes | None], Awaitable[None]]
    ) -> None:
        """
        Call the `callback` function for any change in the KV bucket.

        :param callback: Async function that accepts two arguments: the key of the changed entry (str)
            and its value (bytes). When the value is None, the key has been deleted.
        """
        kv_store = await self._js.key_value(bucket_name.value)
        watcher = await kv_store.watchall()

        while True:
            async for update in watcher:
                # update is of type: nats.js.kv.KeyValue.Entry
                # update.values is the JSON dump of the database entry or None when the key was deleted/purged
                # update.operation is the type of operation that triggered the change
                if not update:
                    continue
                await callback(update.key, None if update.operation in {KV_DEL, KV_PURGE} else update.value)
