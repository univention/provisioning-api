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

    subscribers = "subscribers"

    def stream(subscriber_name: str) -> str:
        return f"stream:{subscriber_name}"

    def durable_name(subscriber_name: str) -> str:
        return f"durable_name:{subscriber_name}"

    def bucket_stream(bucket: str) -> str:
        return f"KV_{bucket}"

    def subscriber(subscriber_name: str) -> str:
        return f"subscriber:{subscriber_name}"


class NatsAdapter:
    def __init__(self):
        self.nats = NATS()
        self.js = self.nats.jetstream()
        self.kv_store: Optional[KeyValue] = None

    async def close(self):
        await self.nats.close()

    async def create_kv_store(self):
        self.kv_store = await self.js.create_key_value(bucket="Pub_Sub_KV")

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
            subscriber_name,
            json.dumps(flat_message).encode("utf-8"),
            stream=stream_name,
        )
        logger.info("Message was published")

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        """Retrieve multiple messages from a NATS subject."""

        try:
            await self.js.stream_info(NatsKeys.stream(subscriber_name))
        except NotFoundError:
            return []

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

    async def delete_stream(self, subscriber_name: str):
        """Delete the entire stream for a given subject in NATS JetStream."""
        await self.js.delete_stream(NatsKeys.stream(subscriber_name))

    async def get_subscriber_names(self):
        kv_store = await self.js.key_value("Pub_Sub_KV")
        try:
            names = await kv_store.get(NatsKeys.subscribers)
        except KeyNotFoundError:
            return []
        return names.value.decode("utf-8").split(",")

    async def add_subscriber(
        self,
        name: str,
        realms_topics: List[list[str, str]],
        fill_queue: bool,
        fill_queue_status: str,
    ):
        sub_info = {
            "name": name,
            "realms_topics": realms_topics,
            "fill_queue": int(fill_queue),
            "fill_queue_status": fill_queue_status,
        }
        await self.kv_store.put(
            NatsKeys.subscriber(name), json.dumps(sub_info).encode("utf-8")
        )

        try:
            subs = await self.kv_store.get(NatsKeys.subscribers)
            updated_subs = subs.value.decode("utf-8") + f",{name}"
            await self.kv_store.put(NatsKeys.subscribers, updated_subs.encode("utf-8"))
        except KeyNotFoundError:
            await self.kv_store.put(NatsKeys.subscribers, name.encode("utf-8"))

        for realm, topic in realms_topics:
            await self.kv_store.put(f"{realm}:{topic}", name.encode("utf-8"))

    async def get_subscriber_info(self, name: str):
        try:
            sub = await self.kv_store.get(NatsKeys.subscriber(name))
            return json.loads(sub.value.decode("utf-8"))
        except KeyNotFoundError:
            return None
