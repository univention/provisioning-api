# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from __future__ import annotations

import contextlib
from typing import Any, AsyncGenerator, Awaitable, Callable, Optional

from server.adapters.nats_adapter import Acknowledgements, NatsKVAdapter, NatsMQAdapter
from univention.provisioning.models import Bucket, Message, MQMessage, Subscription

from .config import DispatcherSettings, dispatcher_settings


class DispatcherPort:
    def __init__(self, settings: Optional[DispatcherSettings] = None):
        self.settings = settings or dispatcher_settings()
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()

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
        await self.mq_adapter.connect(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )
        await self.kv_adapter.init(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
            buckets=[Bucket.subscriptions],
        )

    async def close(self) -> None:
        await self.mq_adapter.close()
        await self.kv_adapter.close()

    async def send_message_to_subscription(self, stream: str, subject: str, message: Message) -> None:
        await self.mq_adapter.add_message(stream, subject, message)

    async def initialize_subscription(self, stream: str, manual_delete: bool, subject: str):
        return await self.mq_adapter.initialize_subscription(stream, manual_delete, subject)

    async def get_one_message(self, timeout: float) -> tuple[MQMessage, Acknowledgements]:
        return await self.mq_adapter.get_one_message(timeout=timeout)

    async def acknowledge_message(self, message: MQMessage) -> None:
        await self.mq_adapter.acknowledge_message(message)

    async def acknowledge_message_in_progress(self, message: MQMessage) -> None:
        await self.mq_adapter.acknowledge_message_in_progress(message)

    async def get_all_subscriptions(self) -> AsyncGenerator[Subscription, None]:
        async for sub in self.kv_adapter.get_all_subscriptions():
            yield sub

    async def watch_for_subscription_changes(self, callback: Callable[[str, Optional[bytes]], Awaitable[None]]) -> None:
        await self.kv_adapter.watch_for_subscription_changes(callback)
