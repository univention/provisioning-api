# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from typing import List, Annotated, Optional, Union

from fastapi import Depends
from fastapi.security import HTTPBasic

from admin.config import AdminSettings
from shared.adapters.nats_adapter import NatsMQAdapter
from shared.adapters.nats_adapter import NatsKVAdapter
from shared.models import Message

from shared.models.queue import PrefillMessage
from shared.models.subscription import Bucket

security = HTTPBasic()


class AdminPort:
    def __init__(self, settings: Optional[AdminSettings] = None):
        self.settings = settings or AdminSettings()
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()

    @staticmethod
    async def port_dependency():
        port = AdminPort()
        await port.mq_adapter.connect(
            user=port.settings.admin_nats_user,
            password=port.settings.admin_nats_password,
        )
        await port.kv_adapter.init(
            buckets=[Bucket.subscriptions, Bucket.credentials],
            user=port.settings.admin_nats_user,
            password=port.settings.admin_nats_password,
        )
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()

    async def get_dict_value(self, name: str, bucket: Bucket) -> Optional[dict]:
        result = await self.kv_adapter.get_value(name, bucket)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def get_list_value(self, key: str, bucket: Bucket) -> List[str]:
        result = await self.kv_adapter.get_value(key, bucket)
        return result.value.decode("utf-8").split(",") if result else []

    async def get_str_value(self, key: str, bucket: Bucket) -> Optional[str]:
        result = await self.kv_adapter.get_value(key, bucket)
        return result.value.decode("utf-8") if result else None

    async def put_value(self, key: str, value: Union[str, dict], bucket: Bucket):
        await self.kv_adapter.put_value(key, value, bucket)

    async def create_stream(self, subject):
        await self.mq_adapter.create_stream(subject)

    async def create_consumer(self, subject):
        await self.mq_adapter.create_consumer(subject)

    async def add_message(self, subject: str, message: Union[Message, PrefillMessage]):
        await self.mq_adapter.add_message(subject, message)

    async def get_bucket_keys(self, bucket: Bucket):
        return await self.kv_adapter.get_keys(bucket)


AdminPortDependency = Annotated[AdminPort, Depends(AdminPort.port_dependency)]
