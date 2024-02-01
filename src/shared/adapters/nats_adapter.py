# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import logging

import json
from typing import List, Union, Optional

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig
from nats.js.errors import NotFoundError, KeyNotFoundError, BucketNotFoundError
from nats.js.kv import KeyValue

from shared.models.queue import NatsMessage, BaseMessage


class NatsKeys:
    """A list of keys used in Nats for queueing messages."""

    def stream(subject: str) -> str:
        return f"stream:{subject}"

    def durable_name(subject: str) -> str:
        return f"durable_name:{subject}"

    def bucket_stream(bucket: str) -> str:
        return f"KV_{bucket}"


class NatsAdapter:
    def __init__(self):
        self.nats = NATS()
        self.js = self.nats.jetstream()
        self.message_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)

    async def close(self):
        await self.nats.close()

    async def create_kv_store(self, bucket: str = "main"):
        if await self.get_kv_store(bucket) is None:
            self.logger.info("Creating bucket with the name: %s", bucket)
            await self.js.create_key_value(bucket=bucket)

    async def add_message(self, subject: str, message: BaseMessage):
        """Publish a message to a NATS subject."""
        flat_message = message.model_dump()
        stream_name = NatsKeys.stream(subject)

        await self.js.publish(
            subject,
            json.dumps(flat_message).encode("utf-8"),
            stream=stream_name,
        )
        self.logger.info("Message was published to %s", stream_name)

    async def get_messages(
        self, subject: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        """Retrieve multiple messages from a NATS subject."""

        try:
            await self.js.stream_info(NatsKeys.stream(subject))
        except NotFoundError:
            return []

        sub = await self.js.pull_subscribe(
            subject,
            durable=NatsKeys.durable_name(subject),
            stream=NatsKeys.stream(subject),
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
                NatsMessage(
                    subject=msg.subject, reply=msg.reply, data=data, headers=msg.headers
                )
            )

        return msgs_to_return

    async def remove_message(self, msg: Union[Msg, NatsMessage]):
        """Delete a message from a NATS JetStream."""
        if isinstance(msg, NatsMessage):
            msg.data["body"] = json.dumps(msg.data["body"])
            msg.data = json.dumps(msg.data)
            msg = Msg(
                _client=self.nats,
                subject=msg.subject,
                reply=msg.reply,
                data=msg.data.encode("utf-8"),
                headers=msg.headers,
            )
        await msg.ack()

    async def delete_stream(self, stream_name: str):
        """Delete the entire stream for a given name in NATS JetStream."""
        try:
            await self.js.delete_stream(NatsKeys.stream(stream_name))
        except NotFoundError:
            return None

    async def delete_consumer(self, subject: str):
        try:
            await self.js.delete_consumer(
                NatsKeys.stream(subject), NatsKeys.durable_name(subject)
            )
        except NotFoundError:
            return None

    async def delete_kv_pair(self, key: str, bucket: str):
        kv_store = await self.get_kv_store(bucket)
        if kv_store:
            await kv_store.delete(key)

    async def get_value(self, key: str, bucket: str) -> Optional[KeyValue.Entry]:
        kv_store = await self.get_kv_store(bucket)
        if kv_store:
            try:
                return await kv_store.get(key)
            except KeyNotFoundError:
                pass
        return None

    async def put_value(self, key: str, value: Union[str, dict], bucket: str):
        kv_store = await self.get_kv_store(bucket)
        if kv_store is None:
            return

        if not value:
            await self.delete_kv_pair(key, bucket)
            return

        if isinstance(value, dict):
            value = json.dumps(value)
        await kv_store.put(key, value.encode("utf-8"))

    async def cb(self, msg):
        await self.message_queue.put(msg)

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.create_stream(subject)
        await self.create_consumer(subject, deliver_subject)

        await self.js.subscribe(
            subject, cb=self.cb, durable=deliver_subject, manual_ack=True
        )

    async def wait_for_event(self) -> Msg:
        return await self.message_queue.get()

    async def stream_exists(self, subject: str) -> bool:
        try:
            await self.js.stream_info(NatsKeys.stream(subject))
        except NotFoundError:
            return False
        return True

    async def get_kv_store(self, bucket: str) -> Optional[KeyValue]:
        try:
            return await self.js.key_value(bucket)
        except BucketNotFoundError:
            self.logger.warning("Bucket with the name: '%s' was not found", bucket)
            return None

    async def create_stream(self, subject: str):
        stream_name = NatsKeys.stream(subject)
        try:
            await self.js.stream_info(stream_name)
            self.logger.info("A stream with the name '%s' already exists", stream_name)
        except NotFoundError:
            self.logger.info("Creating new stream with the name %s", stream_name)
            await self.js.add_stream(name=stream_name, subjects=[subject])

    async def create_consumer(
        self, subject: str, deliver_subject: Optional[str] = None
    ):
        stream_name = NatsKeys.stream(subject)
        durable_name = NatsKeys.durable_name(subject)

        try:
            await self.js.consumer_info(stream_name, durable_name)
            self.logger.info(
                "A consumer with the name '%s' already exists", durable_name
            )
        except NotFoundError:
            self.logger.info("Creating new consumer with the name %s", durable_name)
            await self.js.add_consumer(
                stream_name,
                ConsumerConfig(
                    durable_name=durable_name, deliver_subject=deliver_subject
                ),
            )

    async def get_keys(self, bucket: str) -> List[str]:
        kv_store = await self.get_kv_store(bucket)
        if kv_store is None:
            return []
        return await kv_store.keys()

    async def delete_kv_store(self, bucket: str):
        try:
            await self.js.delete_key_value(bucket)
        except NotFoundError:
            return None
