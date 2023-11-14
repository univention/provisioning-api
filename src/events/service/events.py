from datetime import datetime
from typing import Optional

import core.models

from ..port import MQlibPort
from ..adapters.mq_abstract_adapter import MQAbstractAdapter


class EventsService:

    def __init__(self):
        self._mq = MQlibPort()


    async def publish_event(
        self,
        data: core.models.NewMessage,
        publisher_name: str,
        ts: Optional[datetime] = None,
    ):
        """Publish the given message to all subscribers
           to the given message type.

        :param dict content: Key-value pairs to sent to the consumer.
        :param str publisher_name: The name of the publisher.
        :param datetime ts: Optional timestamp to be assigned to the message.
        """

        message = core.models.Message(
            publisher_name=publisher_name,
            ts=ts or datetime.utcnow(),
            realm=data.realm,
            topic=data.topic,
            body=data.body,
        )

        self._mq.add_message(message)
