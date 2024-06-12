# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from typing import List, Optional, Union, Annotated
from fastapi import Depends
from server.core.app.config import AppSettings
from server.adapters.nats_adapter import NatsMessageQueue, NatsKVStore
from univention.provisioning.models import (
    ProvisioningMessage,
    PrefillMessage,
    Bucket,
    Message,
)
from server.adapters.ports import KVStore, MessageQueue


class Port:  # This is not a port. What is the purpose of this class?
    def __init__(self, settings: Optional[AppSettings] = None):
        self.settings = settings or AppSettings()
        self.mq: MessageQueue = NatsMessageQueue()  # use interface, so implementation is interchangeable
        self.kv: KVStore = NatsKVStore()

    @staticmethod
    async def port_dependency():
        port = Port()
        await port.mq.connect(
            server=port.settings.nats_server,
            user=port.settings.nats_user,
            password=port.settings.nats_password,
        )
        await port.kv.init(
            [Bucket.subscriptions, Bucket.credentials],
            user=port.settings.nats_user,
            password=port.settings.nats_password,
        )
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq.close()
        await self.kv.close()

    async def add_message(
        self, stream: str, subject: str, message: Union[Message, PrefillMessage]
    ):
        await self.mq.add_message(stream, subject, message)  # parameter 'binary_encoder' unfilled

    async def get_message(
        self, stream: str, subject: str, timeout: float, pop: bool
    ) -> Optional[ProvisioningMessage]:
        return await self.mq.get_message(stream, subject, timeout, pop)

    async def delete_message(self, stream: str, seq_num: int):
        await self.mq.delete_message(stream, seq_num)

    async def delete_stream(self, stream_name: str):
        await self.mq.delete_stream(stream_name)

    async def get_dict_value(self, name: str, bucket: Bucket) -> Optional[dict]:
        result = await self.kv.get_value(name, bucket)
        return json.loads(result) if result else None  # 'result' is of type 'Entry'

    async def get_list_value(self, key: str, bucket: Bucket) -> List[str]:
        result = await self.kv.get_value(key, bucket)
        return json.loads(result) if result else []  # 'result' is of type 'Entry'

    async def get_str_value(self, key: str, bucket: Bucket) -> Optional[str]:
        return await self.kv.get_value(key, bucket)

    async def delete_kv_pair(self, key: str, bucket: Bucket):
        await self.kv.delete_kv_pair(key, bucket)

    async def put_value(self, key: str, value: Union[str, dict, list], bucket: Bucket):
        await self.kv.put_value(key, value, bucket)

    async def create_stream(self, stream: str, subjects: List[str]):
        await self.mq.ensure_stream(stream, subjects)  # unexpected argument 'subjects'

    async def stream_exists(self, prefill_queue_name: str) -> bool:
        return await self.mq.stream_exists(prefill_queue_name)

    async def delete_consumer(self, stream_name: str):
        await self.mq.delete_consumer(stream_name)  # unresolved attribute 'delete_consumer' for class 'MessageQueue'

    async def get_bucket_keys(self, bucket: Bucket):
        return await self.kv.get_keys(bucket)  # unresolved reference 'get_keys' for class 'KVStore'

    async def create_consumer(self, subject):
        await self.mq.ensure_consumer(subject)


PortDependency = Annotated[Port, Depends(Port.port_dependency)]
