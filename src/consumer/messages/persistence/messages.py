from typing import Annotated, Dict, List, Optional, Tuple

import fastapi
import json
import redis.asyncio as Redis
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrTimeout

from consumer.core.persistence.nats import NatsDependency
from consumer.core.persistence.redis import RedisDependency


class Keys:
    """A list of keys used in Redis for queueing messages."""

    def queue(subscriber_name):
        return f"queue:{subscriber_name}"


#
# class RedisMessageRepository:
#     """Store and retrieve messages from Redis."""
#
#     def __init__(self, redis: redis.Redis):
#         self._redis = redis
#
#     async def add_live_message(
#         self, subscriber_name: str, message: core.models.Message
#     ):
#         """Enqueue the given message for a particular subscriber.
#
#         The message is received "live" and placed at the end of the queue
#         (i.e. with the current timestamp).
#
#         :param str subscriber_name: Name of the subscriber.
#         :param core.models.Message message: The message from the publisher.
#         """
#
#         key = Keys.queue(subscriber_name)
#         flat_message = message.flatten()
#         await self._redis.xadd(key, flat_message, "*")
#
#     async def add_prefill_message(
#         self, subscriber_name: str, message: core.models.Message
#     ):
#         """Enqueue the given message for a particular subscriber.
#
#         The message originates from the pre-fill process and is queued
#         ahead of (== earlier than) live messages.
#
#         :param str subscriber_name: Name of the subscriber.
#         :param core.models.Message message: The message from the pre-fill task.
#         """
#
#         key = Keys.queue(subscriber_name)
#         flat_message = message.flatten()
#         await self._redis.xadd(key, flat_message, "0-*")
#
#     async def delete_prefill_messages(self, subscriber_name: str):
#         """Delete all pre-fill messages from the subscriber's queue."""
#         key = Keys.queue(subscriber_name)
#         await self._redis.xtrim(key, minid=1)
#
#     async def get_next_message(
#         self, subscriber_name: str, block: Optional[int] = None
#     ) -> Optional[Tuple[str, core.models.Message]]:
#         """Retrieve the first message from the subscriber's stream.
#
#         :param str subscriber_id: Id of the subscriber.
#         :param int block: How long to block in milliseconds if no message is available.
#         """
#         key = Keys.queue(subscriber_name)
#
#         response = await self._redis.xread({key: "0-0"}, count=1, block=block)
#
#         if key not in response:
#             # empty stream
#             return None
#
#         entries = response[key][0]
#         if entries:
#             message_id, flat_message = cast(Tuple[str, Dict[str, str]], entries[0])
#             message = core.models.Message.inflate(flat_message)
#             return (message_id, message)
#
#     async def get_messages(
#         self,
#         subscriber_name: str,
#         count: Optional[int] = None,
#         first: int | str = "-",
#         last: int | str = "+",
#     ) -> List[Tuple[str, core.models.Message]]:
#         """Return messages from a given queue.
#
#         By default, *all* messages will be returned unless further restricted by
#         parameters.
#
#         :param str subscriber_id: Id of the subscriber.
#         :param int count: How many messages to return at most.
#         :param str first: Id of the first message to return.
#         :param str last: Id of the last message to return.
#         """
#         key = Keys.queue(subscriber_name)
#
#         response = await self._redis.xrange(key, first, last, count)
#
#         return [
#             (message_id, core.models.Message.inflate(flat_message))
#             for message_id, flat_message in response
#         ]
#
#     async def delete_message(self, subscriber_name: str, message_id: str):
#         """Remove a message from the subscriber's queue.
#
#         :param str subscriber_id: Id of the subscriber.
#         :param str message_id: Id of the message to delete.
#         """
#
#         key = Keys.queue(subscriber_name)
#         await self._redis.xdel(key, message_id)
#
#     async def delete_queue(self, subscriber_name: str):
#         """Delete the entire queue for the given consumer.
#
#         :param str subscriber_id: Id of the subscriber.
#         """
#
#         key = Keys.queue(subscriber_name)
#         await self._redis.xtrim(key, maxlen=0)


class MessageRepository:
    """Store and retrieve messages from NATS."""

    def __init__(self, nats: NATS, redis: Redis):
        self._nats = nats
        self._redis = redis

    async def add_message(self, subject: str, message: Dict[str, str]):
        """Publish a message to a NATS subject."""
        await self._nats.publish(subject, json.dumps(message).encode())

    async def get_message(self, subject: str) -> Optional[Dict[str, str]]:
        """Retrieve a message from a NATS subject."""
        try:
            msg = await self._nats.request(subject, timeout=1)
            return json.loads(msg.data.decode())
        except ErrTimeout:
            return None

    async def get_messages(self, subject: str, count: int) -> List[Dict[str, str]]:
        """Retrieve multiple messages from a NATS subject."""
        messages = []
        for _ in range(count):
            msg = await self.get_message(subject)
            if msg:
                messages.append(msg)
        return messages

    async def delete_message(self, subject: str, msg_seq: str):
        """Delete a message from a NATS JetStream."""
        await self._nats.jetstream().delete_msg(subject, int(msg_seq))

    async def get_next_message(
        self, subject: str
    ) -> Optional[Tuple[str, Dict[str, str]]]:
        """Retrieve the next message from a NATS JetStream."""
        try:
            info = await self._nats.jetstream().get_last_msg(subject)
            return info.seq, json.loads(info.data.decode())
        except ErrTimeout:
            return None

    async def add_live_message(self, subject: str, message: Dict[str, str]):
        """Publish a message to a NATS JetStream."""
        await self.add_message(subject, message)

    async def add_prefill_message(self, subject: str, message: Dict[str, str]):
        """Publish a prefill message to a NATS JetStream."""
        # Note: You might need to customize this according to your prefill logic
        await self.add_message(subject, message)

    async def delete_prefill_messages(self, subject: str):
        """Delete all prefill messages from a NATS JetStream."""
        # Note: You will need to implement a logic to identify and delete prefill messages

    async def delete_queue(self, subject: str):
        """Delete the entire stream for a given subject in NATS JetStream."""
        await self._nats.jetstream().delete_stream(subject)


# def get_message_repository(redis: RedisDependency) -> MessageRepository:
#     return MessageRepository(redis)


def get_message_repository(
    nats: NatsDependency, redis: RedisDependency
) -> MessageRepository:
    return MessageRepository(nats, redis)


DependsMessageRepo = Annotated[
    MessageRepository, fastapi.Depends(get_message_repository)
]
