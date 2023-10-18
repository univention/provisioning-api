from typing import Annotated, Dict, cast, List, Optional, Tuple

import core.models
import fastapi
import aio_pika
import redis.asyncio as redis
from core.models import Message
from kafka import KafkaProducer, KafkaConsumer

from .redis import RedisDependency


class Keys:
    """A list of keys used in Redis for queueing messages."""

    def queue(subscriber_name):
        return f"queue:{subscriber_name}"


class MessageRepository:
    """Store and retrieve messages from Redis."""

    def __init__(self, redis: redis.Redis):
        self._redis = redis

    async def add_live_message(
        self, subscriber_name: str, message: core.models.Message
    ):
        """Enqueue the given message for a particular subscriber.

        The message is received "live" and placed at the end of the queue
        (i.e. with the current timestamp).

        :param str subscriber_name: Name of the subscriber.
        :param core.models.Message message: The message from the publisher.
        """

        key = Keys.queue(subscriber_name)
        flat_message = message.flatten()
        await self._redis.xadd(key, flat_message, "*")

    async def add_prefill_message(
        self, subscriber_name: str, message: core.models.Message
    ):
        """Enqueue the given message for a particular subscriber.

        The message originates from the pre-fill process and is queued
        ahead of (== earlier than) live messages.

        :param str subscriber_name: Name of the subscriber.
        :param core.models.Message message: The message from the pre-fill task.
        """

        key = Keys.queue(subscriber_name)
        flat_message = message.flatten()
        await self._redis.xadd(key, flat_message, "0-*")

    async def delete_prefill_messages(self, subscriber_name: str):
        """Delete all pre-fill messages from the subscriber's queue."""
        key = Keys.queue(subscriber_name)
        await self._redis.xtrim(key, minid=1)

    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[Tuple[str, core.models.Message]]:
        """Retrieve the first message from the subscriber's stream.

        :param str subscriber_id: Id of the subscriber.
        :param int block: How long to block in milliseconds if no message is available.
        """
        key = Keys.queue(subscriber_name)

        response = await self._redis.xread({key: "0-0"}, count=1, block=block)

        if key not in response:
            # empty stream
            return None

        entries = response[key][0]
        if entries:
            message_id, flat_message = cast(Tuple[str, Dict[str, str]], entries[0])
            message = core.models.Message.inflate(flat_message)
            return (message_id, message)

    async def get_messages(
        self,
        subscriber_name: str,
        count: Optional[int] = None,
        first: int | str = "-",
        last: int | str = "+",
    ) -> List[Tuple[str, core.models.Message]]:
        """Return messages from a given queue.

        By default, *all* messages will be returned unless further restricted by
        parameters.

        :param str subscriber_id: Id of the subscriber.
        :param int count: How many messages to return at most.
        :param str first: Id of the first message to return.
        :param str last: Id of the last message to return.
        """
        key = Keys.queue(subscriber_name)

        response = await self._redis.xrange(key, first, last, count)

        return [
            (message_id, core.models.Message.inflate(flat_message))
            for message_id, flat_message in response
        ]

    async def delete_message(self, subscriber_name: str, message_id: str):
        """Remove a message from the subscriber's queue.

        :param str subscriber_id: Id of the subscriber.
        :param str message_id: Id of the message to delete.
        """

        key = Keys.queue(subscriber_name)
        await self._redis.xdel(key, message_id)

    async def delete_queue(self, subscriber_name: str):
        """Delete the entire queue for the given consumer.

        :param str subscriber_id: Id of the subscriber.
        """

        key = Keys.queue(subscriber_name)
        await self._redis.xtrim(key, maxlen=0)


class RabbitMQMessageRepository(MessageRepository):
    """
    Message repository using RabbitMQ as a backend.
    Concerns:
    - RabbitMQ alwaus appends message in the end. There's no api to prepend messages or control the insert position.
    - RabbitMQ does not provide a direct mechanism to selectively delete messages by content or position in the queue.

    As a prefill workaround, we will use two separate queues - one for pre-fill messages and one for live messages.
    The consumer can first process all messages from the prefill queue before moving on to the live queue.

    """

    live_queue_prefix = "live_"
    prefill_queue_prefix = "prefill_"

    def __init__(self, connection: aio_pika.Connection):
        self._connection = connection

    async def _get_channel(self) -> aio_pika.Channel:
        return await self._connection.channel()

    async def add_live_message(self, subscriber_name: str, message: Message):
        channel = await self._get_channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.flatten_bytes()),
            f"{self.prefill_queue_prefix}{subscriber_name}",
        )

    async def add_prefill_message(self, subscriber_name: str, message: Message):
        channel = await self._get_channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=message.flatten_bytes()),
            f"{self.prefill_queue_prefix}{subscriber_name}",
        )

    async def delete_prefill_messages(self, subscriber_name: str):
        channel = await self._get_channel()
        await channel.queue_delete(f"{self.prefill_queue_prefix}{subscriber_name}")

    async def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[Tuple[str, Message]]:
        channel = await self._get_channel()

        # Check prefill queue first
        prefill_queue = await channel.declare_queue(
            f"{self.prefill_queue_prefix}{subscriber_name}", auto_delete=True
        )
        live_queue = await channel.declare_queue(
            f"{self.live_queue_prefix}{subscriber_name}", auto_delete=True
        )

        if prefill_queue.message_count > 0:
            message: aio_pika.IncomingMessage = await prefill_queue.get(timeout=block)
        else:
            message: aio_pika.IncomingMessage = await live_queue.get(timeout=block)

        return message.message_id, Message.inflate(message.body.decode())

    async def get_messages(
        self,
        subscriber_name: str,
        count: Optional[int] = None,
        first: int | str = "-",
        last: int | str = "+",
    ) -> List[Tuple[str, Message]]:
        messages = []
        channel = await self._get_channel()

        prefill_queue = await channel.declare_queue(
            f"{self.prefill_queue_prefix}{subscriber_name}", auto_delete=True
        )
        live_queue = await channel.declare_queue(
            f"{self.live_queue_prefix}{subscriber_name}", auto_delete=True
        )

        total_count = count or (prefill_queue.message_count + live_queue.message_count)

        for _ in range(total_count):
            if prefill_queue.message_count > 0:
                message: aio_pika.IncomingMessage = await prefill_queue.get()
            else:
                message: aio_pika.IncomingMessage = await live_queue.get()
                if not message:
                    break
            messages.append(
                (message.message_id, Message.inflate(message.body.decode()))
            )

        return messages

    async def delete_message(self, subscriber_name: str, message_id: str):
        # Deleting individual messages in RabbitMQ by their ID is not supported, we need to consume instead.
        pass

    async def delete_queue(self, subscriber_name: str):
        channel = await self._get_channel()
        prefill_queue = await channel.declare_queue(
            f"{self.prefill_queue_prefix}{subscriber_name}", auto_delete=True
        )
        live_queue = await channel.declare_queue(
            f"{self.live_queue_prefix}{subscriber_name}", auto_delete=True
        )
        await prefill_queue.delete(if_unused=False, if_empty=False)
        await live_queue.delete(if_unused=False, if_empty=False)


class KafkaMessageRepository(MessageRepository):
    live_queue_prefix = "live_"
    prefill_queue_prefix = "prefill_"

    def __init__(self, bootstrap_servers: List[str]):
        self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        self.consumer = KafkaConsumer(bootstrap_servers=bootstrap_servers)

    def add_live_message(self, subscriber_name: str, message: Message):
        self.producer.send(
            f"{self.live_queue_prefix}{subscriber_name}", value=message.flatten()
        )

    def add_prefill_message(self, subscriber_name: str, message: Message):
        self.producer.send(
            f"{self.prefill_queue_prefix}{subscriber_name}", value=message.flatten()
        )

    def delete_prefill_messages(self, subscriber_name: str):
        # Kafka doesn't allow for direct deletion of messages.
        # In real-world scenarios, one might consider using Kafka's log compaction or topic deletion.
        pass

    def get_next_message(
        self, subscriber_name: str, block: Optional[int] = None
    ) -> Optional[Tuple[str, Message]]:
        # block is ignored
        # Check prefill topic first
        self.consumer.subscribe(
            [
                f"{self.prefill_queue_prefix}{subscriber_name}",
                f"{self.live_queue_prefix}{subscriber_name}",
            ]
        )

        for record in self.consumer:
            # Deserialize and return the next message
            return record.offset, Message.inflate(record.value)

        return None

    def get_messages(
        self, subscriber_name: str, count: Optional[int] = None
    ) -> List[Tuple[str, Message]]:
        # first and last args are not supported
        self.consumer.subscribe(
            [
                f"{self.prefill_queue_prefix}{subscriber_name}",
                f"{self.live_queue_prefix}{subscriber_name}",
            ]
        )

        messages = []
        for _, record in zip(range(count), self.consumer):
            messages.append((record.offset, Message.inflate(record.value)))

        return messages

    def delete_message(self, subscriber_name: str, offset: int):
        # Kafka also doesn't support direct message deletion.
        pass

    def delete_queue(self, subscriber_name: str):
        # Kafka uses topics, not queues. Deleting a topic is possible but typically
        # managed outside of client applications due to data integrity concerns.
        # It's generally recommended to create new topics instead of deleting old ones.
        # Resources:
        # https://stackoverflow.com/questions/32703469/python-how-to-delete-all-messages-under-a-kafka-topic
        # https://martinhynar.medium.com/strategies-for-deletion-of-records-in-kafka-topic-c13f2fbe0f82
        # https://kafka.apache.org/documentation.html#compaction
        pass


def get_message_repository(redis: RedisDependency) -> MessageRepository:
    return MessageRepository(redis)


DependsMessageRepo = Annotated[
    MessageRepository, fastapi.Depends(get_message_repository)
]
