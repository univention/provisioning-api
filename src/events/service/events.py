import logging

from events.port import EventsPort

from shared.models import Message

logger = logging.getLogger(__name__)


class EventsService:
    def __init__(self, port: EventsPort):
        self._port = port

    async def publish_event(
        self,
        event: Message,
    ):
        """Publish the given message to all subscribers
           to the given message type.

        :param Message event: Key-value pairs to sent to the consumer.
        """

        await self._port.add_live_event(event)
