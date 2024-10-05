# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from contextlib import asynccontextmanager
from typing import Annotated, List, Optional, Union

from fastapi import Depends

from univention.provisioning.backends import key_value_store, message_queue
from univention.provisioning.models.constants import Bucket
from univention.provisioning.models.message import Message, PrefillMessage, ProvisioningMessage

from .config import AppSettings, app_settings


class Port:
    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings or app_settings()
        self.mq_adapter = message_queue(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
        )
        self.kv_adapter = key_value_store(
            server=self.settings.nats_server,
            user=self.settings.nats_user,
            password=self.settings.nats_password,
        )

    @staticmethod
    async def port_dependency():
        port = Port()
        await port.connect()
        try:
            yield port
        finally:
            await port.close()

    @staticmethod
    @asynccontextmanager
    async def port_context():
        port = Port()
        await port.connect()
        try:
            yield port
        finally:
            await port.close()

    async def connect(self):
        await self.mq_adapter.connect()
        await self.kv_adapter.init(buckets=[Bucket.subscriptions, Bucket.credentials])

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()

    async def add_message(self, stream: str, subject: str, message: Union[Message, PrefillMessage]):
        await self.mq_adapter.add_message(stream, subject, message)

    async def get_message(self, stream: str, subject: str, timeout: float, pop: bool) -> Optional[ProvisioningMessage]:
        return await self.mq_adapter.get_message(stream, subject, timeout, pop)

    async def delete_message(self, stream: str, seq_num: int):
        await self.mq_adapter.delete_message(stream, seq_num)

    async def delete_stream(self, stream_name: str):
        await self.mq_adapter.delete_stream(stream_name)

    async def get_dict_value(self, name: str, bucket: Bucket) -> Optional[dict]:
        result = await self.kv_adapter.get_value(name, bucket)
        return json.loads(result) if result else None

    async def get_list_value(self, key: str, bucket: Bucket) -> List[str]:
        result = await self.kv_adapter.get_value(key, bucket)
        return json.loads(result) if result else []

    async def get_str_value(self, key: str, bucket: Bucket) -> Optional[str]:
        return await self.kv_adapter.get_value(key, bucket)

    async def delete_kv_pair(self, key: str, bucket: Bucket):
        await self.kv_adapter.delete_kv_pair(key, bucket)

    async def put_value(self, key: str, value: Union[str, dict, list], bucket: Bucket, revision: Optional[int] = None):
        await self.kv_adapter.put_value(key, value, bucket, revision)

    async def ensure_stream(self, stream: str, manual_delete: bool, subjects: List[str] | None = None):
        await self.mq_adapter.ensure_stream(stream, manual_delete, subjects)

    async def stream_exists(self, prefill_queue_name: str) -> bool:
        return await self.mq_adapter.stream_exists(prefill_queue_name)

    async def delete_consumer(self, stream_name: str):
        await self.mq_adapter.delete_consumer(stream_name)

    async def get_bucket_keys(self, bucket: Bucket):
        return await self.kv_adapter.get_keys(bucket)

    async def ensure_consumer(self, subject):
        await self.mq_adapter.ensure_consumer(subject)


PortDependency = Annotated[Port, Depends(Port.port_dependency)]
