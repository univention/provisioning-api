# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from __future__ import annotations

import contextlib
from typing import Any, AsyncGenerator, Awaitable, Callable, Optional

from univention.provisioning.backends import key_value_store, message_queue
from univention.provisioning.models.constants import Bucket
from univention.provisioning.models.message import Message, MQMessage
from univention.provisioning.models.subscription import Subscription

from .config import DispatcherSettings, dispatcher_settings


class DispatcherPort:
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        self.settings = settings or dispatcher_settings()
        self.mq = message_queue(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )
        self.kv = key_value_store(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
        )

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context() -> AsyncGenerator[DispatcherPort, Any]:
        port = DispatcherPort()
        await port.connect()
        try:
            yield port
        finally:
            await port.close()

    async def connect(self) -> None:
        await self.mq.connect()
        await self.kv.init(buckets=[Bucket.subscriptions])

    async def close(self) -> None:
        await self.mq.close()
        await self.kv.close()

    async def send_message_to_subscription(self, stream: str, subject: str, message: Message) -> None:
        await self.mq.add_message(stream, subject, message)

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str):
        return await self.mq.initialize_subscription(stream, manual_delete, subject)

    async def get_one_message(self, timeout: float) -> tuple[MQMessage, message_queue.Acknowledgements]:
        return await self.mq.get_one_message(timeout=timeout)

    async def acknowledge_message(self, message: MQMessage) -> None:
        await self.mq.acknowledge_message(message)

    async def acknowledge_message_in_progress(self, message: MQMessage) -> None:
        await self.mq.acknowledge_message_in_progress(message)

    async def get_all_subscriptions(self) -> AsyncGenerator[Subscription, None]:
        async for sub in self.kv.get_all_subscriptions():
            yield sub

    async def watch_for_subscription_changes(self, callback: Callable[[str, Optional[bytes]], Awaitable[None]]) -> None:
        await self.kv.watch_for_subscription_changes(callback)
