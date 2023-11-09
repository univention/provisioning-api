import asyncio
import logging

import json
from typing import List

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig
from nats.js.errors import NotFoundError

from core.models import Message

logger = logging.getLogger(__name__)


class NatsKeys:
    """A list of keys used in Nats for queueing messages."""

    def stream(subscriber_name):
        return f"stream:{subscriber_name}"

    def durable_name(subscriber_name):
        return f"durable_name:{subscriber_name}"


class NatsAdapter:
    def __init__(self, nats: NATS):
        self.nats = nats
        self.js = self.nats.jetstream()

    async def add_message(self, subscriber_name: str, message: Message):
        """Publish a message to a NATS subject."""
        flat_message = message.flatten()
        stream_name = NatsKeys.stream(subscriber_name)
        try:
            await self.js.stream_info(stream_name)
        except NotFoundError:
            logger.warning(f"Creating new stream with name: {stream_name}")
            await self.js.add_stream(name=stream_name, subjects=[subscriber_name])

        await self.js.add_consumer(
            stream_name,
            ConsumerConfig(durable_name=NatsKeys.durable_name(subscriber_name)),
        )
        await self.js.publish(
            subscriber_name, json.dumps(flat_message).encode(), stream=stream_name
        )
        logger.info("Message was published")

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ):
        """Retrieve multiple messages from a NATS subject."""
        sub = await self.js.pull_subscribe(
            subscriber_name,
            durable=f"durable_name:{subscriber_name}",
            stream=NatsKeys.stream(subscriber_name),
        )
        try:
            msgs = await sub.fetch(count, timeout)
        except asyncio.TimeoutError:
            return []

        if pop:
            await self.delete_messages(msgs)

        return [Message.inflate(json.loads(ms.data.decode("utf-8"))) for ms in msgs]

    async def delete_messages(self, msgs: List[Msg]):
        """Delete a message from a NATS JetStream."""
        for msg in msgs:
            await msg.ack()

    async def delete_stream(self, subscriber_name: str):
        """Delete the entire stream for a given subject in NATS JetStream."""
        await self.js.delete_stream(NatsKeys.stream(subscriber_name))
