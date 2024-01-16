# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import List, Annotated, Optional, Union

from fastapi import Depends

from shared.adapters.nats_adapter import NatsMQAdapter
from shared.adapters.nats_adapter import NatsKVAdapter
from shared.models import Message

from shared.models.queue import NatsMessage


class ConsumerPort:
    def __init__(self):
        self.message_queue = NatsMQAdapter()
        self.kv_store = NatsKVAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = ConsumerPort()
        await port.message_queue.connect()
        await port.kv_store.connect()
        try:
            yield port
        finally:
            await port.close()

    @staticmethod
    async def port_dependency():
        port = ConsumerPort()
        await port.message_queue.connect()
        await port.kv_store.connect()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.message_queue.close()
        await self.kv_store.close()

    async def add_live_message(self, subject: str, message: Message):
        await self.message_queue.add_message(subject, message)

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        pass

    async def delete_prefill_messages(self, subscriber_name: str):
        pass

    async def get_next_message(
        self, subscriber_name: str, timeout: float, pop: bool
    ) -> List[NatsMessage]:
        return await self.message_queue.get_messages(subscriber_name, timeout, 1, pop)

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        return await self.message_queue.get_messages(
            subscriber_name, timeout, count, pop
        )

    async def remove_message(self, msg: NatsMessage):
        await self.message_queue.remove_message(msg)

    async def delete_queue(self, stream_name: str):
        await self.message_queue.delete_stream(stream_name)

    async def get_dict_value(self, name: str) -> Optional[dict]:
        result = await self.kv_store.get_value(name)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def get_list_value(self, key: str) -> List[str]:
        result = await self.kv_store.get_value(key)
        return result.value.decode("utf-8").split(",") if result else []

    async def get_str_value(self, key: str) -> Optional[str]:
        result = await self.kv_store.get_value(key)
        return result.value.decode("utf-8") if result else None

    async def delete_kv_pair(self, key: str):
        await self.kv_store.delete_kv_pair(key)

    async def put_value(self, key: str, value: Union[str, dict]):
        await self.kv_store.put_value(key, value)

    async def put_list_value(self, key: str, value: list[str]):
        await self.kv_store.put_value(key, ",".join(value))


ConsumerPortDependency = Annotated[ConsumerPort, Depends(ConsumerPort.port_dependency)]
