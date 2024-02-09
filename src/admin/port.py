# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
from typing import List, Annotated, Optional, Union

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from shared.adapters.nats_adapter import NatsMQAdapter
from shared.adapters.nats_adapter import NatsKVAdapter
from shared.models import Message

from shared.models.queue import PrefillMessage

security = HTTPBasic()


class AdminPort:
    def __init__(self):
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()

    @staticmethod
    async def port_dependency(
            credentials: Annotated[HTTPBasicCredentials, Depends(security)]
    ):
        port = AdminPort()
        await port.mq_adapter.connect(credentials)
        await port.kv_adapter.connect(credentials)
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()

    async def get_dict_value(self, name: str) -> Optional[dict]:
        result = await self.kv_adapter.get_value(name)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def get_list_value(self, key: str) -> List[str]:
        result = await self.kv_adapter.get_value(key)
        return result.value.decode("utf-8").split(",") if result else []

    async def get_str_value(self, key: str) -> Optional[str]:
        result = await self.kv_adapter.get_value(key)
        return result.value.decode("utf-8") if result else None

    async def put_value(self, key: str, value: Union[str, dict]):
        await self.kv_adapter.put_value(key, value)

    async def create_stream(self, subject):
        await self.mq_adapter.create_stream(subject)

    async def create_consumer(self, subject):
        await self.mq_adapter.create_consumer(subject)

    async def add_message(self, subject: str, message: Union[Message, PrefillMessage]):
        await self.mq_adapter.add_message(subject, message)


AdminPortDependency = Annotated[AdminPort, Depends(AdminPort.port_dependency)]
