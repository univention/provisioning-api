# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib
import json
from typing import List, Annotated, Optional, Union

from fastapi import Depends

from shared.adapters.nats_adapter import NatsAdapter
from shared.adapters.redis_adapter import RedisAdapter
from shared.config import settings
from shared.models import Message

from shared.models.queue import NatsMessage, PrefillMessage


class ConsumerPort:
    def __init__(self):
        self.redis_adapter = RedisAdapter()
        self.nats_adapter = NatsAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = ConsumerPort()
        await port.nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port.nats_adapter.create_kv_store()
        try:
            yield port
        finally:
            await port.close()

    @staticmethod
    async def port_dependency():
        port = ConsumerPort()
        await port.nats_adapter.nats.connect(
            servers=[f"nats://{settings.nats_host}:{settings.nats_port}"]
        )
        await port.nats_adapter.create_kv_store()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.redis_adapter.close()
        await self.nats_adapter.close()

    async def add_message(self, subject: str, message: Union[Message, PrefillMessage]):
        await self.nats_adapter.add_message(subject, message)

    async def delete_prefill_messages(self, subscriber_name: str):
        await self.redis_adapter.delete_prefill_messages(subscriber_name)

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        return await self.nats_adapter.get_messages(
            subscriber_name, timeout, count, pop
        )

    async def remove_message(self, msg: NatsMessage):
        await self.nats_adapter.remove_message(msg)

    async def delete_stream(self, stream_name: str):
        await self.nats_adapter.delete_stream(stream_name)

    async def delete_consumer(self, stream_name: str):
        await self.nats_adapter.delete_consumer(stream_name)

    async def get_dict_value(self, name: str, bucket: str) -> Optional[dict]:
        result = await self.nats_adapter.get_value(name, bucket)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def get_list_value(self, key: str, bucket: str) -> List[str]:
        result = await self.nats_adapter.get_value(key, bucket)
        return result.value.decode("utf-8").split(",") if result else []

    async def get_str_value(self, key: str, bucket: str) -> Optional[str]:
        result = await self.nats_adapter.get_value(key, bucket)
        return result.value.decode("utf-8") if result else None

    async def delete_kv_pair(self, key: str, bucket: str):
        await self.nats_adapter.delete_kv_pair(key, bucket)

    async def put_value(self, key: str, value: Union[str, dict], bucket: str):
        await self.nats_adapter.put_value(key, value, bucket)

    async def put_list_value(self, key: str, value: List[str], bucket: str):
        await self.nats_adapter.put_value(key, ",".join(value), bucket)

    async def stream_exists(self, prefill_queue_name: str) -> bool:
        return await self.nats_adapter.stream_exists(prefill_queue_name)

    async def create_stream(self, subject):
        await self.nats_adapter.create_stream(subject)

    async def create_consumer(self, subject):
        await self.nats_adapter.create_consumer(subject)

    async def get_subscription_names(self, bucket: str) -> List[str]:
        return await self.nats_adapter.get_keys(bucket)

    async def subscriber_exists(self, bucket: str):
        return await self.nats_adapter.get_kv_store(bucket)

    async def create_subscriber(self, name: str):
        await self.nats_adapter.create_kv_store(name)

    async def delete_subscriber(self, name: str):
        await self.nats_adapter.delete_kv_store(name)


ConsumerPortDependency = Annotated[ConsumerPort, Depends(ConsumerPort.port_dependency)]
