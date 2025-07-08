# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
from typing import AsyncGenerator, Awaitable, Callable, Optional

from univention.provisioning.backends_core.constants import BucketName
from univention.provisioning.backends_core.nats_kv import NatsKeyValueDB
from univention.provisioning.models.subscription import Subscription

from .config import DispatcherSettings, dispatcher_settings
from .subscriptions_port import SubscriptionsPort

logger = logging.getLogger(__file__)


class NatsSubscriptionsAdapter(SubscriptionsPort):
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        self.settings = settings or dispatcher_settings()
        self.kv = NatsKeyValueDB(self.settings)

    async def __aenter__(self) -> SubscriptionsPort:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.close()
        return False

    async def connect(self) -> None:
        await self.kv.init(buckets=[BucketName.subscriptions])

    async def close(self) -> None:
        await self.kv.close()

    async def get_all_subscriptions(self) -> AsyncGenerator[Subscription, None]:
        async for key, value in self.kv.get_bucket_items(BucketName.subscriptions):
            try:
                subscription_dict = json.loads(value.decode("utf-8"))
                subscription = Subscription.model_validate(subscription_dict)
            except (ValueError, AttributeError) as exc:
                logger.error("Bad subscription data in KV store. key=%r entry=%r exc=%s", key, value, exc)
                raise
            yield subscription

    async def watch_for_subscription_changes(self, callback: Callable[[str, Optional[bytes]], Awaitable[None]]) -> None:
        await self.kv.watch_for_changes_in_bucket(BucketName.subscriptions, callback)
