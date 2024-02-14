# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
from typing import List, Annotated, Optional, Union

from fastapi import Depends

from shared.adapters.nats_adapter import NatsMQAdapter
from shared.adapters.nats_adapter import NatsKVAdapter
from shared.models import Message

from shared.models.queue import MQMessage
from shared.models.queue import PrefillMessage
from shared.models.subscription import Bucket


class ConsumerPort:
    def __init__(self):
        self.mq_adapter = NatsMQAdapter()
        self.kv_adapter = NatsKVAdapter()

    @staticmethod
    async def port_dependency():
        port = ConsumerPort()
        await port.mq_adapter.connect()
        await port.kv_adapter.setup_nats_and_kv(
            [Bucket.subscriptions, Bucket.credentials]
        )
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()
        await self.kv_adapter.close()

    async def add_message(self, subject: str, message: Union[Message, PrefillMessage]):
        await self.mq_adapter.add_message(subject, message)

    async def delete_prefill_messages(self, subscription_name: str):
        pass

    async def get_messages(
        self, subscription_name: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        return await self.mq_adapter.get_messages(
            subscription_name, timeout, count, pop
        )

    async def remove_message(self, msg: MQMessage):
        await self.mq_adapter.remove_message(msg)

    async def delete_stream(self, stream_name: str):
        await self.mq_adapter.delete_stream(stream_name)

    async def get_dict_value(self, name: str, bucket: Bucket) -> Optional[dict]:
        result = await self.kv_adapter.get_value(name, bucket)
        return json.loads(result.value.decode("utf-8")) if result else None

    async def get_list_value(self, key: str, bucket: Bucket) -> List[str]:
        result = await self.kv_adapter.get_value(key, bucket)
        return result.value.decode("utf-8").split(",") if result else []

    async def delete_kv_pair(self, key: str, bucket: Bucket):
        await self.kv_adapter.delete_kv_pair(key, bucket)

    async def put_value(self, key: str, value: Union[str, dict], bucket: Bucket):
        await self.kv_adapter.put_value(key, value, bucket)

    async def put_list_value(self, key: str, value: list[str], bucket: Bucket):
        await self.kv_adapter.put_value(key, ",".join(value), bucket)

    async def create_stream(self, subject):
        await self.mq_adapter.create_stream(subject)

    async def stream_exists(self, prefill_queue_name: str) -> bool:
        return await self.mq_adapter.stream_exists(prefill_queue_name)

    async def delete_consumer(self, stream_name: str):
        await self.mq_adapter.delete_consumer(stream_name)


ConsumerPortDependency = Annotated[ConsumerPort, Depends(ConsumerPort.port_dependency)]
