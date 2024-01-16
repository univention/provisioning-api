# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import logging

import json
from typing import List, Union, Optional

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig
from nats.js.errors import NotFoundError, KeyNotFoundError
from nats.js.kv import KeyValue

from shared.adapters.base_adapters import BaseKVStoreAdapter, BaseMQAdapter
from shared.config import settings
from shared.models import Message
from shared.models.queue import MQMessage


class NatsKeys:
    """A list of keys used in Nats for queueing messages."""

    def stream(subject: str) -> str:
        return f"stream:{subject}"

    def durable_name(subject: str) -> str:
        return f"durable_name:{subject}"

    def bucket_stream(bucket: str) -> str:
        return f"KV_{bucket}"


class NatsKVAdapter(BaseKVStoreAdapter):
    def __init__(self):
        self._nats = NATS()
        self._js = self._nats.jetstream()
        self._kv_store: Optional[KeyValue] = None
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        await self._nats.connect([settings.nats_server])
        await self.create_kv_store()

    async def close(self):
        await self._nats.close()

    async def create_kv_store(self, name: str = "Pub_Sub_KV"):
        self._kv_store = await self._js.create_key_value(bucket=name)

    async def delete_kv_pair(self, key: str):
        await self._kv_store.delete(key)

    async def get_value(self, key: str) -> Optional[KeyValue.Entry]:
        try:
            return await self._kv_store.get(key)
        except KeyNotFoundError:
            return None

    async def put_value(self, key: str, value: Union[str, dict]):
        if not value:
            await self.delete_kv_pair(key)  # Avoid creating a pair with an empty value
            return

        if isinstance(value, dict):
            value = json.dumps(value)
        await self._kv_store.put(key, value.encode("utf-8"))


class NatsMQAdapter(BaseMQAdapter):
    def __init__(self):
        self._nats = NATS()
        self._js = self._nats.jetstream()
        self._message_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)

    async def connect(self):
        await self._nats.connect([settings.nats_server])

    async def close(self):
        await self._nats.close()

    async def add_message(self, subject: str, message: Message):
        """Publish a message to a NATS subject."""
        flat_message = message.model_dump()
        stream_name = NatsKeys.stream(subject)
        try:
            await self._js.stream_info(stream_name)
        except NotFoundError:
            self.logger.debug("Creating new stream with name: %s", stream_name)
            await self._js.add_stream(name=stream_name, subjects=[subject])

        await self._js.add_consumer(
            stream_name,
            ConsumerConfig(durable_name=NatsKeys.durable_name(subject)),
        )
        await self._js.publish(
            subject,
            json.dumps(flat_message).encode("utf-8"),
            stream=stream_name,
        )
        self.logger.info("Message was published")

    async def get_messages(
        self, subject: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        """Retrieve multiple messages from a NATS subject."""

        try:
            await self._js.stream_info(NatsKeys.stream(subject))
        except NotFoundError:
            return []

        sub = await self._js.pull_subscribe(
            subject, durable=f"durable_name:{subject}", stream=NatsKeys.stream(subject)
        )
        try:
            msgs = await sub.fetch(count, timeout)
        except asyncio.TimeoutError:
            return []

        if pop:
            for msg in msgs:
                await self.remove_message(msg)

        msgs_to_return = []
        for msg in msgs:
            data = json.loads(msg.data)
            msgs_to_return.append(
                MQMessage(
                    subject=msg.subject, reply=msg.reply, data=data, headers=msg.headers
                )
            )

        return msgs_to_return

    async def remove_message(self, msg: Union[Msg, MQMessage]):
        """Delete a message from a NATS JetStream."""
        if isinstance(msg, MQMessage):
            msg.data["body"] = json.dumps(msg.data["body"])
            msg.data = json.dumps(msg.data)
            msg = Msg(
                _client=self._nats,
                subject=msg.subject,
                reply=msg.reply,
                data=msg.data.encode("utf-8"),
                headers=msg.headers,
            )
        await msg.ack()

    async def delete_stream(self, stream_name: str):
        """Delete the entire stream for a given name in NATS JetStream."""
        try:
            await self._js.stream_info(NatsKeys.stream(stream_name))
            await self._js.delete_stream(NatsKeys.stream(stream_name))
        except NotFoundError:
            return None

    async def cb(self, msg):
        await self._message_queue.put(msg)

    async def subscribe_to_queue(self, subject):
        await self._nats.subscribe(subject, cb=self.cb)

    async def wait_for_event(self) -> Msg:
        return await self._message_queue.get()
