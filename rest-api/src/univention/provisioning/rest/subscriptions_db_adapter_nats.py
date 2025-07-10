# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json

from univention.provisioning.backends_core.constants import BucketName
from univention.provisioning.backends_core.key_value_db import KeyValueDB
from univention.provisioning.backends_core.nats_kv import NatsKeyValueDB
from univention.provisioning.models.subscription import Subscription

from .config import AppSettings
from .subscriptions_db_port import NoSubscription, SubscriptionsDBPort

PREFILL_FAILURES_STREAM = "prefill-failures"
PREFILL_DURABLE_NAME = "prefill-service"


class NatsSubscriptionsDB(SubscriptionsDBPort):
    """
    Handle communication with key-value DB.

    Use as an async context manager.
    """

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self._kv_store: KeyValueDB = NatsKeyValueDB(self.settings)

    async def __aenter__(self) -> SubscriptionsDBPort:
        await self._kv_store.init(buckets=[BucketName.subscriptions, BucketName.credentials])
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self._kv_store.close()
        return False

    async def get_dict_value(self, name: str, bucket: BucketName) -> dict | None:
        result = await self._kv_store.get_value(name, bucket)
        return json.loads(result) if result else None

    async def get_list_value(self, key: str, bucket: BucketName) -> list[str]:
        result = await self._kv_store.get_value(key, bucket)
        return json.loads(result) if result else []

    async def get_str_value(self, key: str, bucket: BucketName) -> str | None:
        return await self._kv_store.get_value(key, bucket)

    async def delete_kv_pair(self, key: str, bucket: BucketName):
        await self._kv_store.delete_kv_pair(key, bucket)

    async def put_value(self, key: str, value: str | dict | list, bucket: BucketName, revision: int | None = None):
        await self._kv_store.put_value(key, value, bucket, revision)

    async def get_bucket_keys(self, bucket: BucketName) -> list[str]:
        return await self._kv_store.get_keys(bucket)

    async def delete_subscription(self, name: str) -> None:
        await self.delete_kv_pair(name, BucketName.credentials)
        await self.delete_kv_pair(name, BucketName.subscriptions)

    async def load_hashed_password(self, name: str) -> str:
        return await self.get_str_value(name, BucketName.credentials)

    async def load_subscription(self, name: str) -> Subscription | None:
        """
        :raises NoSubscription: if subscription was not found.
        """
        if result := await self.get_dict_value(name, BucketName.subscriptions):
            return Subscription.model_validate(result)
        else:
            raise NoSubscription(f"Subscription not found: {name!r}")

    async def load_subscription_names(self):
        return await self.get_bucket_keys(BucketName.credentials)

    async def store_hashed_password(self, name: str, password: str) -> None:
        await self.put_value(name, password, BucketName.credentials)

    async def store_subscription(self, name: str, subscription: Subscription) -> None:
        await self.put_value(name, subscription.model_dump(), BucketName.subscriptions)
