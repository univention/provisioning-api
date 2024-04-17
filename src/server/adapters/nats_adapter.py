# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import json
import logging
from typing import List, Optional, Union, Dict

from nats.aio.client import Client as NATS
from nats.aio.msg import Msg
from nats.js.api import ConsumerConfig
from nats.js.errors import (
    BucketNotFoundError,
    KeyNotFoundError,
    NoKeysError,
    NotFoundError,
    ServerError,
)
from nats.js.kv import KV_DEL

from .base_adapters import BaseKVStoreAdapter, BaseMQAdapter
from ..config import settings
from shared.models import (
    BaseMessage,
    ProvisioningMessage,
    MQMessage,
    Bucket,
    REALM_TOPIC_PREFIX,
)

MAX_RECONNECT_ATTEMPTS = 5


class NatsKeys:
    """A list of keys used in Nats for queueing messages."""

    def stream(subject: str) -> str:
        return f"stream:{subject}"

    def durable_name(subject: str) -> str:
        return f"durable_name:{subject}"


class NatsKVAdapter(BaseKVStoreAdapter):
    def __init__(self):
        self._nats = NATS()
        self._js = self._nats.jetstream()
        self.logger = logging.getLogger(__name__)

    async def init(self, buckets: List[Bucket], user: str, password: str):
        await self._nats.connect(
            [settings.nats_server],
            user=user,
            password=password,
            max_reconnect_attempts=1,
        )
        for bucket in buckets:
            await self.create_kv_store(bucket)

    async def close(self):
        await self._nats.close()

    async def create_kv_store(self, bucket: Bucket):
        try:
            await self._js.key_value(bucket.value)
        except BucketNotFoundError:
            self.logger.info("Creating bucket with the name: %s", bucket)
            await self._js.create_key_value(bucket=bucket.value)

    async def delete_kv_pair(self, key: str, bucket: Bucket):
        kv_store = await self._js.key_value(bucket.value)
        await kv_store.delete(key)

    async def get_value(self, key: str, bucket: Bucket) -> Optional[str]:
        kv_store = await self._js.key_value(bucket.value)
        try:
            result = await kv_store.get(key)
            return result.value.decode("utf-8") if result else None
        except KeyNotFoundError:
            pass

    async def put_value(self, key: str, value: Union[str, dict, list], bucket: Bucket):
        kv_store = await self._js.key_value(bucket.value)

        if not value:
            # Avoid creating a pair with an empty value
            await self.delete_kv_pair(key, bucket)
            return

        if not isinstance(value, str):
            value = json.dumps(value)
        await kv_store.put(key, value.encode("utf-8"))

    async def get_keys(self, bucket: Bucket) -> List[str]:
        kv_store = await self._js.key_value(bucket.value)
        try:
            return await kv_store.keys()
        except NoKeysError:
            return []

    async def watch_for_changes(self, subscriptions: Dict[str, list]):
        kv_store = await self._js.key_value(Bucket.subscriptions.value)
        watcher = await kv_store.watch(f"{REALM_TOPIC_PREFIX}.*", include_history=True)

        while True:
            async for update in watcher:
                if update:
                    _, realm_topic = update.key.split(".", maxsplit=1)
                    if update.operation == KV_DEL:
                        subscriptions.pop(realm_topic, None)
                    else:
                        updated_subscriptions = json.loads(update.value.decode("utf-8"))
                        subscriptions[realm_topic] = updated_subscriptions
                    self.logger.info("Subscriptions were updated: %s", subscriptions)


class NatsMQAdapter(BaseMQAdapter):
    def __init__(self):
        self._nats = NATS()
        self._js = self._nats.jetstream()
        self.logger = logging.getLogger(__name__)
        self._message_queue = asyncio.Queue()

    async def connect(self, user: str, password: str, **kwargs):
        """Connect to the NATS server.

        Arguments are passed directly to the NATS client.
        https://nats-io.github.io/nats.py/modules.html#asyncio-client
        """
        await self._nats.connect(
            [settings.nats_server], user=user, password=password, **kwargs
        )

    async def close(self):
        await self._nats.close()

    async def add_message(self, stream: str, subject: str, message: BaseMessage):
        """Publish a message to a NATS subject."""
        stream_name = NatsKeys.stream(stream)

        await self._js.publish(
            subject,
            json.dumps(message.model_dump()).encode("utf-8"),
            stream=stream_name,
        )
        self.logger.info(
            "Message was published to the stream: %s with the subject: %s",
            stream_name,
            subject,
        )

    async def get_messages(
        self, stream: str, subject: str, timeout: float, count: int, pop: bool
    ) -> List[ProvisioningMessage]:
        """Retrieve multiple messages from a NATS subject."""

        stream_name = NatsKeys.stream(stream)
        durable_name = NatsKeys.durable_name(stream)

        try:
            await self._js.stream_info(stream_name)
        except NotFoundError:
            self.logger.error("The stream was not found")
            return []

        consumer = await self._js.consumer_info(stream_name, durable_name)

        sub = await self._js.pull_subscribe(
            subject, durable=durable_name, stream=stream_name, config=consumer
        )
        try:
            msgs = await sub.fetch(count, timeout)
        except asyncio.TimeoutError:
            return []

        if pop:
            for msg in msgs:
                await msg.ack()

        msgs_to_return = [self.provisioning_message_from(msg) for msg in msgs]
        return msgs_to_return

    @staticmethod
    def provisioning_message_from(msg: Msg) -> ProvisioningMessage:
        data = json.loads(msg.data)
        sequence_number = msg.reply.split(".")[-4]
        message = ProvisioningMessage(
            sequence_number=sequence_number,
            num_delivered=msg.metadata.num_delivered,
            publisher_name=data["publisher_name"],
            ts=data["ts"],
            realm=data["realm"],
            topic=data["topic"],
            body=data["body"],
        )
        return message

    def nats_message_from(self, message: MQMessage) -> Msg:
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
    def mq_message_from(msg: Msg) -> MQMessage:
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

    async def delete_consumer(self, subject: str):
        try:
            await self._js.delete_consumer(
                NatsKeys.stream(subject), NatsKeys.durable_name(subject)
            )
        except NotFoundError:
            return None

    async def cb(self, msg):
        await self._message_queue.put(msg)

    async def subscribe_to_queue(self, subject: str, deliver_subject: str):
        await self.create_stream(subject)
        await self.create_consumer(subject, deliver_subject)

        await self._js.subscribe(
            subject,
            cb=self.cb,
            durable=NatsKeys.durable_name(subject),
            stream=NatsKeys.stream(subject),
            manual_ack=True,
        )

    async def wait_for_event(self) -> MQMessage:
        msg = await self._message_queue.get()
        message = self.mq_message_from(msg)
        return message

    async def stream_exists(self, subject: str) -> bool:
        try:
            await self._js.stream_info(NatsKeys.stream(subject))
        except NotFoundError:
            return False
        return True

    async def create_stream(self, stream: str, subjects: List[str] = None):
        stream_name = NatsKeys.stream(stream)
        try:
            await self._js.stream_info(stream_name)
            self.logger.info("A stream with the name '%s' already exists", stream_name)
        except NotFoundError:
            await self._js.add_stream(name=stream_name, subjects=subjects or [stream])
            self.logger.info("A stream with the name '%s' was created", stream_name)

    async def create_consumer(
        self, subject: str, deliver_subject: Optional[str] = None
    ):
        stream_name = NatsKeys.stream(subject)
        durable_name = NatsKeys.durable_name(subject)

        try:
            await self._js.consumer_info(stream_name, durable_name)
            self.logger.info(
                "A consumer with the name '%s' already exists", durable_name
            )
        except NotFoundError:
            await self._js.add_consumer(
                stream_name,
                ConsumerConfig(
                    durable_name=durable_name,
                    deliver_subject=deliver_subject,
                    max_ack_pending=1,
                ),
            )
            self.logger.info("A consumer with the name '%s' was created", durable_name)

    async def acknowledge_message(self, message: MQMessage):
        msg = self.nats_message_from(message)
        await msg.ack()

    async def acknowledge_message_negatively(self, message: MQMessage):
        msg = self.nats_message_from(message)
        await msg.nak()

    async def acknowledge_message_in_progress(self, message: MQMessage):
        msg = self.nats_message_from(message)
        await msg.in_progress()

    async def delete_message(self, stream: str, subject: str, seq_num: int):
        self.logger.info("Deleting message from the stream: %s", stream)
        try:
            await self._js.get_msg(NatsKeys.stream(stream), seq_num, subject=subject)
            await self._js.delete_msg(NatsKeys.stream(stream), seq_num)
            self.logger.info("Message was deleted")
        except ServerError as exc:
            self.logger.error("Failed to delete the message: %s", exc.description)

    async def purge_subject_from_messages(self, stream: str, subject: str):
        await self._js.purge_stream(NatsKeys.stream(stream), subject=subject)
