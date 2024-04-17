# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from typing import List, Annotated, Optional, Union
from fastapi import Depends
from server.core.app.config import AppSettings
from server.adapters.nats_adapter import NatsMQAdapter, NatsKVAdapter
from shared.models import ProvisioningMessage, PrefillMessage, Bucket, Message


class Port:
    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings or AppSettings()
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()

    @staticmethod
    async def port_dependency():
        port = Port()
        await port.mq_adapter.connect(
            user=port.settings.nats_user, password=port.settings.nats_password
        )
        await port.kv_adapter.init(
            [Bucket.subscriptions, Bucket.credentials],
            user=port.settings.nats_user,
            password=port.settings.nats_password,
        )
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()

    async def add_message(
        self, stream: str, subject: str, message: Union[Message, PrefillMessage]
    ):
        await self.mq_adapter.add_message(stream, subject, message)

    async def get_message(
        self, stream: str, subject: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        return await self.mq_adapter.get_message(stream, subject, timeout, pop)

    async def delete_message(self, stream: str, subject: str, seq_num: int):
        await self.mq_adapter.delete_message(stream, subject, seq_num)

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

    async def put_value(self, key: str, value: Union[str, dict, list], bucket: Bucket):
        await self.kv_adapter.put_value(key, value, bucket)

    async def create_stream(self, stream: str, subjects: List[str]):
        await self.mq_adapter.create_stream(stream, subjects)

    async def stream_exists(self, prefill_queue_name: str) -> bool:
        return await self.mq_adapter.stream_exists(prefill_queue_name)

    async def delete_consumer(self, stream_name: str):
        await self.mq_adapter.delete_consumer(stream_name)

    async def get_bucket_keys(self, bucket: Bucket):
        return await self.kv_adapter.get_keys(bucket)

    async def create_consumer(self, subject):
        await self.mq_adapter.create_consumer(subject)


PortDependency = Annotated[Port, Depends(Port.port_dependency)]
