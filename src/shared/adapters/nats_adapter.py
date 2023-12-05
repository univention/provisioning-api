import asyncio
import logging

import json
from typing import List, Union, Optional

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig
from nats.js.errors import NotFoundError, KeyNotFoundError
from nats.js.kv import KeyValue

from shared.models import Message
from shared.models.queue import NatsMessage

logger = logging.getLogger(__name__)


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
        self.kv_store: Optional[KeyValue] = None

    async def close(self):
        await self.nats.close()

    async def create_kv_store(self):
        self.kv_store = await self.js.create_key_value(bucket="Pub_Sub_KV")

    async def add_message(self, subject: str, message: Message):
        """Publish a message to a NATS subject."""
        flat_message = message.flatten()
        stream_name = NatsKeys.stream(subject)
        try:
            await self.js.stream_info(stream_name)
        except NotFoundError:
            logger.warning(f"Creating new stream with name: {stream_name}")
            await self.js.add_stream(name=stream_name, subjects=[subject])

        await self.js.add_consumer(
            stream_name,
            ConsumerConfig(durable_name=NatsKeys.durable_name(subject)),
        )
        await self.js.publish(
            subject,
            json.dumps(flat_message).encode("utf-8"),
            stream=stream_name,
        )
        logger.info("Message was published")

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
            durable=f"durable_name:{subject}",
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
            data["body"] = json.loads(data["body"])
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

    async def delete_stream(self, subject: str):
        """Delete the entire stream for a given subject in NATS JetStream."""
        try:
            await self.js.stream_info(NatsKeys.stream(subject))
            await self.js.delete_stream(NatsKeys.stream(subject))
        except NotFoundError:
            return None

    async def delete_kv_pair(self, key: str):
        await self.kv_store.delete(key)

    async def get_value(self, key: str) -> Optional[KeyValue.Entry]:
        try:
            return await self.kv_store.get(key)
        except KeyNotFoundError:
            return None

    async def put_value(self, key: str, value: Union[str, dict]):
        if not value:
            await self.delete_kv_pair(key)
            return

        if isinstance(value, dict):
            value = json.dumps(value)
        await self.kv_store.put(key, value.encode("utf-8"))
