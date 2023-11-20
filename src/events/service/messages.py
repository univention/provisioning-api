import logging
from datetime import datetime
from typing import Optional

from events.port import EventsPort

from shared.models.queue import Message
from shared.models import NewMessage

logger = logging.getLogger(__name__)


class MessageService:
    def __init__(self, port: EventsPort):
        self._port = port

    async def publish_message(
        self,
        data: NewMessage,
        publisher_name: str,
        ts: Optional[datetime] = None,
    ):
        """Publish the given message to all subscribers
           to the given message type.

        :param NewMessage data: Key-value pairs to sent to the consumer.
        :param str publisher_name: The name of the publisher.
        :param datetime ts: Optional timestamp to be assigned to the message.
        """

        message = Message(
            publisher_name=publisher_name,
            ts=ts or datetime.utcnow(),
            realm=data.realm,
            topic=data.topic,
            body=data.body,
        )

        await self._port.add_live_message(message)
