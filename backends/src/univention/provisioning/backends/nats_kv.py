# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
from typing import AsyncGenerator, Awaitable, Callable, List, Optional, Tuple, Union

from nats.aio.client import Client as NATS
from nats.js.errors import (
    BucketNotFoundError,
    KeyNotFoundError,
    KeyWrongLastSequenceError,
    NotFoundError,
)
from nats.js.kv import KV_DEL, KV_OP, KV_PURGE

from univention.provisioning.models.constants import BucketName
from univention.provisioning.models.subscription import Subscription

from .key_value_db import KeyValueDB, UpdateConflict

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

    @staticmethod
    def _stream_name(bucket: BucketName) -> str:
        # A KV bucket `X` is backed by a JetStream stream named `KV_X`.
        return f"KV_{bucket.value}"

    @staticmethod
    def _subject_prefix(bucket: BucketName) -> str:
        # A KV key `k` in bucket `X` is stored on the subject `$KV.X.k`.
        return f"$KV.{bucket.value}."

    async def _iter_live_entries(self, bucket: BucketName) -> AsyncGenerator[Tuple[str, bytes], None]:
        """
        Enumerate the live (non-deleted) key/value pairs in `bucket` from a consistent snapshot.

        ``KeyValue.keys()`` (and ``watch()``) enumerate via an ephemeral ``last_per_subject``
        consumer whose "caught up" decision relies on the server-reported ``num_pending``. On a
        clustered JetStream server that value is unreliable under concurrent writes, so the
        enumeration can return an empty/partial view and silently drop keys.

        Instead we read a point-in-time snapshot that never consults ``num_pending``:
        - the key set comes from ``stream_info(subjects_filter=...)`` (committed stream state,
          computed server-side);
        - each value comes from ``get_last_msg`` (last message per subject), skipping tombstones
          (keys whose latest operation is a delete/purge but which have not been purged yet).
        """
        stream = self._stream_name(bucket)
        prefix = self._subject_prefix(bucket)
        try:
            info = await self._js.stream_info(stream, subjects_filter=f"{prefix}>")
        except NotFoundError:
            return

        subjects = (info.state.subjects or {}) if info.state else {}
        for subject in subjects:
            try:
                msg = await self._js.get_last_msg(stream, subject)
            except NotFoundError:
                # Key vanished between listing and reading; treat as not present.
                continue

            operation = (msg.headers or {}).get(KV_OP)
            if operation in (KV_DEL, KV_PURGE):
                # Tombstone: key is deleted but not yet purged from the stream.
                continue

            key = subject[len(prefix) :]
            yield key, msg.data

    async def get_keys(self, bucket: BucketName) -> List[str]:
        return [key async for key, _ in self._iter_live_entries(bucket)]

    async def get_all_subscriptions(self) -> AsyncGenerator[Subscription, None]:
        async for key, value in self._iter_live_entries(BucketName.subscriptions):
            try:
                subscription_dict = json.loads(value)
                subscription = Subscription.model_validate(subscription_dict)
            except ValueError as exc:
                logger.error("Bad subscription data in KV store. key=%r value=%r exc=%s", key, value, exc)
                raise
            yield subscription

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
