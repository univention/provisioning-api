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
        self.message_queue = asyncio.Queue()

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
            logger.info(f"Creating new stream with name: {stream_name}")
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
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[NatsMessage]:
        """Retrieve multiple messages from a NATS subject."""

        try:
            await self.js.stream_info(NatsKeys.stream(subscriber_name))
        except NotFoundError:
            return []

        sub = await self.js.pull_subscribe(
            subscriber_name,
            durable=NatsKeys.durable_name(subscriber_name),
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
        try:
            await self.js.stream_info(NatsKeys.stream(subscriber_name))
            await self.js.delete_stream(NatsKeys.stream(subscriber_name))
        except NotFoundError:
            return None

    async def add_subscriber(
        self,
        name: str,
        realm_topic: str,
        fill_queue: bool,
        fill_queue_status: str,
    ):
        sub_info = {
            "name": name,
            "realms_topics": [realm_topic],
            "fill_queue": int(fill_queue),
            "fill_queue_status": fill_queue_status,
        }
        await self.put_value_by_key(NatsKeys.subscriber(name), sub_info)
        await self.update_subscribers_for_key(NatsKeys.subscribers, name)

        await self.update_subscribers_for_key(realm_topic, name)

    async def create_subscription(self, name: str, realm_topic: str, sub_info: dict):
        sub_info["realms_topics"].append(realm_topic)
        await self.put_value_by_key(NatsKeys.subscriber(name), sub_info)
        await self.update_subscribers_for_key(realm_topic, name)

    async def get_subscriber_info(self, name: str) -> Optional[dict]:
        try:
            sub = await self.kv_store.get(NatsKeys.subscriber(name))
            return json.loads(sub.value.decode("utf-8"))
        except KeyNotFoundError:
            return None

    async def set_subscriber_queue_status(self, name: str, sub_info: dict) -> None:
        await self.put_value_by_key(NatsKeys.subscriber(name), sub_info)

    async def delete_subscriber_from_key(self, key: str, name: str):
        subs = await self.get_subscribers_for_key(key)
        subs.remove(name)
        if not subs:
            await self.kv_store.delete(key)
        else:
            await self.put_value_by_key(key, ",".join(subs))

    async def delete_subscriber(self, name: str):
        await self.delete_subscriber_from_key(NatsKeys.subscribers, name)
        await self.kv_store.delete(NatsKeys.subscriber(name))

    async def get_value_by_key(self, key: str) -> Optional[KeyValue.Entry]:
        try:
            return await self.kv_store.get(key)
        except KeyNotFoundError:
            return None

    async def put_value_by_key(self, key: str, value: Union[str, dict]):
        if isinstance(value, dict):
            value = json.dumps(value)
        await self.kv_store.put(key, value.encode("utf-8"))

    async def get_subscribers_for_key(self, key: str):
        names = await self.get_value_by_key(key)
        return names.value.decode("utf-8").split(",") if names else []

    async def update_subscribers_for_key(self, key: str, name: str) -> None:
        try:
            subs = await self.kv_store.get(key)
            updated_subs = subs.value.decode("utf-8") + f",{name}"
            await self.put_value_by_key(key, updated_subs)
        except KeyNotFoundError:
            await self.put_value_by_key(key, name)

    async def get_value(self, key: str) -> Optional[KeyValue.Entry]:
        try:
            return await self.kv_store.get(key)
        except KeyNotFoundError:
            return None

    async def cb(self, msg):
        await self.message_queue.put(msg)

    async def subscribe_to_queue(self, subject):
        await self.nats.subscribe(subject, cb=self.cb)

    async def wait_for_event(self) -> Msg:
        return await self.message_queue.get()
