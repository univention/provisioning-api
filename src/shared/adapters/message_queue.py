import asyncio
import logging

from enum import Enum
from typing import List, Union, Dict

from core.models import Message
from core.models.queue import MQMessage
from core.models.adapters import BaseMessageQueue


logger = logging.getLogger(__name__)


class MessageQueueAdapter:
    """The implementation class for an abstract message queue adapter."""
    def __init__(self, message_queue: BaseMessageQueue):
        self.message_queue = message_queue # NatsAdapter, RabbitMQAdapter etc. | BaseAdapter

    async def add_message(self, subscriber_name: str, message: Message):
        """Publish a message to a subscription subject."""
        return await self.message_queue.add_message(
            subscriber_name=subscriber_name, message=message
        )

    async def get_messages(
        self, subscriber_name: str, timeout: float, count: int, pop: bool
    ) -> List[MQMessage]:
        """Retrieve multiple messages by subscription subject."""

        return await self.message_queue.get_messages(
            subscriber_name=subscriber_name, timeout=timeout, count=count, pop=pop
        )

    async def delete_message(self, msg: MQMessage):
        """Delete a message from a message queue stream."""

        return await self.message_queue.delete_message(msg=msg)

    async def delete_stream(self, subscriber_name: str):
        """Delete the stream for a given subject from the message queue."""

        return await self.message_queue.delete_stream(subscriber_name=subscriber_name)
