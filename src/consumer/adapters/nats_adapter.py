import logging

import json
from nats.aio.client import Client as NATS
from nats.js.errors import NotFoundError

from core.models import Message

logger = logging.getLogger(__name__)


class NatsKeys:
    """A list of keys used in Nats for queueing messages."""

    def stream(subscriber_name):
        return f"stream:{subscriber_name}"


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

        await self.js.publish(subscriber_name, json.dumps(flat_message).encode())
        logger.info("Message was published")

    async def get_messages(self, subscriber_name: str, count: int = 1):
        """Retrieve multiple messages from a NATS subject."""

        sub = await self.js.pull_subscribe(
            subscriber_name, stream=NatsKeys.stream(subscriber_name)
        )
        msgs = await sub.fetch(count)
        return [Message.inflate(json.loads(ms.data.decode("utf-8"))) for ms in msgs]

        # TODO: add error handling

    async def delete_message(self, subject: str, msg_seq: str):
        """Delete a message from a NATS JetStream."""
        # TODO: check whether it works
        await self.nats.jetstream().delete_msg(subject, int(msg_seq))

    async def delete_queue(self, subject: str):
        """Delete the entire stream for a given subject in NATS JetStream."""
        # TODO: check whether it works
        await self.js.delete_stream(subject)
