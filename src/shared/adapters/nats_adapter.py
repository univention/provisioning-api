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

from shared.models.queue import BaseMessage
from shared.adapters.base_adapters import BaseKVStoreAdapter, BaseMQAdapter
from shared.config import settings
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

    async def add_message(self, subject: str, message: BaseMessage):
        """Publish a message to a NATS subject."""

        stream_name = NatsKeys.stream(subject)

        await self._js.publish(
            subject,
            json.dumps(message.model_dump()).encode("utf-8"),
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
            self.logger.error("The stream was not found")
            return []

        sub = await self._js.pull_subscribe(
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
                await msg.ack()

        msgs_to_return = [self.construct_mq_message(msg) for msg in msgs]
        return msgs_to_return

    def construct_nats_message(self, message: MQMessage) -> Msg:
        data = message.data
        msg = Msg(
            _client=self._nats,
            subject=message.subject,
            reply=message.reply,
            data=json.dumps(data).encode("utf-8"),
            headers=message.headers,
        )
        return msg

    @staticmethod
    def construct_mq_message(msg: Msg) -> MQMessage:
        data = json.loads(msg.data)
        sequence_number = msg.reply.split(".")[-4]
        message = MQMessage(
            subject=msg.subject,
            reply=msg.reply,
            data=data,
            headers=msg.headers,
            num_delivered=msg.metadata.num_delivered,
            sequence_number=sequence_number,
        )
        return message

    async def delete_stream(self, stream_name: str):
        """Delete the entire stream for a given name in NATS JetStream."""
        try:
            await self._js.delete_stream(NatsKeys.stream(stream_name))
        except NotFoundError:
            return None

    async def cb(self, msg):
        await self._message_queue.put(msg)

    async def subscribe_to_queue(self, stream_subject: str, deliver_subject: str):
        await self.create_stream(stream_subject)
        await self.create_consumer(stream_subject, deliver_subject)

        await self._js.subscribe(
            stream_subject,
            cb=self.cb,
            durable=NatsKeys.durable_name(stream_subject),
            manual_ack=True,
        )

    async def wait_for_event(self) -> MQMessage:
        msg = await self._message_queue.get()
        message = self.construct_mq_message(msg)
        return message

    async def stream_exists(self, subject: str) -> bool:
        try:
            await self._js.stream_info(NatsKeys.stream(subject))
        except NotFoundError:
            return False
        return True

    async def create_stream(self, subject: str):
        stream_name = NatsKeys.stream(subject)
        try:
            await self._js.stream_info(stream_name)
            self.logger.info("A stream with the name '%s' already exists", stream_name)
        except NotFoundError:
            self.logger.info("Creating new stream with the name %s", stream_name)
            await self._js.add_stream(name=stream_name, subjects=[subject])

    async def create_consumer(
        self, subject: str, deliver_subject: Optional[str] = None
    ):
        stream_name = NatsKeys.stream(subject)
        durable_name = NatsKeys.durable_name(subject)

        try:
            await self._js.consumer_info(stream_name, durable_name)
        except NotFoundError:
            self.logger.info("Creating new consumer with the name %s", durable_name)
            await self._js.add_consumer(
                stream_name,
                ConsumerConfig(
                    durable_name=durable_name, deliver_subject=deliver_subject
                ),
            )

    async def acknowledge_message(self, message: MQMessage):
        msg = self.construct_nats_message(message)
        await msg.ack()

    async def acknowledge_message_negatively(self, message: MQMessage):
        msg = self.construct_nats_message(message)
        await msg.nak()

    async def acknowledge_message_in_progress(self, message: MQMessage):
        msg = self.construct_nats_message(message)
        await msg.in_progress()

    async def delete_message(self, stream_name: str, seq_num: int):
        self.logger.info("Deleting message from the stream: %s", stream_name)
        try:
            await self._js.get_msg(NatsKeys.stream(stream_name), seq_num)
            await self._js.delete_msg(NatsKeys.stream(stream_name), seq_num)
            self.logger.info("Message was deleted")
        except NotFoundError as exc:
            self.logger.error("Failed to delete the message: %s", exc.description)
