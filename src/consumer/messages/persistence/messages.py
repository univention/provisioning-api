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

    async def delete_queue(self, subject: str):
        """Delete the entire stream for a given subject in NATS JetStream."""
        await self._nats.jetstream().delete_stream(subject)


def get_message_repository(
    nats: NatsDependency, redis: RedisDependency
) -> MessageRepository:
    return MessageRepository(nats, redis)


DependsMessageRepo = Annotated[
    MessageRepository, fastapi.Depends(get_message_repository)
]
