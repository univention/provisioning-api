import logging
from datetime import datetime
from typing import Optional

from events.port import EventsPort

from shared.models import Event

logger = logging.getLogger(__name__)


class EventsService:
    def __init__(self, port: EventsPort):
        self._port = port

    async def publish_event(
        self,
        event: Event,
        publisher_name: str,
        ts: Optional[datetime] = None,
    ):
        """Publish the given message to all subscribers
           to the given message type.

        :param Event data: Key-value pairs to sent to the consumer.
        :param str publisher_name: The name of the publisher.
        :param datetime ts: Optional timestamp to be assigned to the message.
        """

        await self._port.add_live_event(event, publisher_name, ts)
