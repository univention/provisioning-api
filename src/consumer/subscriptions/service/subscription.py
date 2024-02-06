# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
import re
from datetime import datetime
from typing import List, Optional

from consumer.port import ConsumerPort
from consumer.subscriptions.subscription.sink import SinkManager
from shared.models import Subscriber, NewSubscriber, FillQueueStatus
from shared.models.queue import PrefillMessage

manager = SinkManager()
SUBSCRIBERS = "subscribers"
REALM_TOPIC_TEMPLATE = "{realm}:{topic}"


def match_subscription(
    sub_realm: str, sub_topic: str, msg_realm: str, msg_topic: str
) -> bool:
    """Decides whether a message is sent to a subscriber.

    Compares the subscriber's realm and topic to those of the message and
    returns `True` if the message should be sent to the subscriber.
    """

    if sub_realm != msg_realm:
        return False

    return re.fullmatch(sub_topic, msg_topic) is not None


class SubscriptionService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def get_subscribers(self) -> List[Subscriber]:
        """
        Return a list of all known subscribers.
        """

        names = await self.get_subscriber_names(SUBSCRIBERS)
        subscribers = [await self.get_subscriber(name) for name in names]

        return subscribers

    async def get_subscriber_names(self, key: str):
        return await self._port.get_list_value(key)

    async def get_subscriber(self, name: str) -> Subscriber:
        """
        Get information about a registered subscriber.
        """
        sub = await self.get_subscriber_info(name)
        if not sub:
            raise ValueError("Subscriber not found.")

        return sub

    async def create_subscriber(self, new_sub: NewSubscriber):
        """
        Add a new subscriber.
        """
        if new_sub.request_prefill:
            prefill_queue_status = FillQueueStatus.pending
        else:
            prefill_queue_status = FillQueueStatus.done

        # realm_topic_str = f"{sub.realm_topic[0]}:{sub.realm_topic[1]}"
        sub_info = await self.get_subscriber_info(new_sub.name)
        if sub_info:
            raise ValueError("Subscriber with the given realm_topic already exists")

        else:
            self.logger.debug("Creating new subscriber with the name: %s", new_sub.name)
            realms_topics_str = [
                REALM_TOPIC_TEMPLATE.format(realm=r, topic=t)
                for r, t in new_sub.realms_topics
            ]
            sub_info = Subscriber(
                name=new_sub.name,
                realms_topics=realms_topics_str,
                request_prefill=new_sub.request_prefill,
                prefill_queue_status=prefill_queue_status,
            )
            await self.set_sub_info(new_sub.name, sub_info)
            await self.add_sub_to_subscribers(new_sub.name)
            await self.update_realm_topic_subscribers(
                sub_info.realms_topics, new_sub.name
            )
            await self._port.create_stream(new_sub.name)
            await self._port.create_consumer(new_sub.name)

            self.logger.info("New subscriber was created")

    async def update_realm_topic_subscribers(self, realms_topics: List[str], name: str):
        for realm_topic in realms_topics:
            await self.update_subscriber_names(realm_topic, name)

    async def get_subscriber_info(self, name: str) -> Optional[Subscriber]:
        result = await self._port.get_dict_value(name)
        return Subscriber.model_validate(result) if result else result

    async def get_subscriber_queue_status(self, name: str) -> FillQueueStatus:
        """Get the pre-fill status of the given subscriber."""

        sub_info = await self.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber was not found.")

        return sub_info.prefill_queue_status

    async def set_subscriber_queue_status(self, name: str, status: FillQueueStatus):
        """Set the pre-fill status of the given subscriber."""
        sub_info = await self.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber was not found.")

        sub_info.prefill_queue_status = status.name
        await self.set_sub_info(name, sub_info)

    async def set_sub_info(self, name, sub_info: Subscriber):
        await self._port.put_value(name, sub_info.model_dump())

    async def delete_subscriber(self, name: str):
        """
        Delete a subscriber and all of its data.
        """

        sub_info = await self.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber was not found.")

        for realm_topic in sub_info.realms_topics:
            await self.delete_sub_from_realm_topic(realm_topic, name)

        await self.delete_sub_from_subscribers(name)
        await self.delete_sub_info(name)
        await self._port.delete_stream(name)
        await self._port.delete_consumer(name)

    async def delete_sub_from_subscribers(self, name: str):
        await self.delete_subscriber_from_values(SUBSCRIBERS, name)

    async def delete_sub_from_realm_topic(self, realm_topic_str: str, name: str):
        await self.delete_subscriber_from_values(realm_topic_str, name)

    async def delete_sub_info(self, name: str):
        await self._port.delete_kv_pair(name)

    async def delete_subscriber_from_values(self, key: str, name: str):
        self.logger.debug("Deleting subscriber %s from %s", name, key)

        subs = await self._port.get_list_value(key)
        if not subs:
            raise ValueError("There are no subscribers")

        if name not in subs:
            raise ValueError("The subscriber with the given name does not exist")

        subs.remove(name)
        await self._port.put_list_value(key, subs)

        self.logger.info("Subscriber was deleted")

    async def update_subscriber_names(self, key: str, value: str) -> None:
        subs = await self._port.get_str_value(key)
        if subs:
            value = subs + f",{value}"
        await self._port.put_value(key, value)

    async def add_sub_to_subscribers(self, name: str):
        await self.update_subscriber_names(SUBSCRIBERS, name)

    async def send_request_to_prefill(self, subscriber: NewSubscriber):
        self.logger.info("Sending the requests to prefill")
        message = PrefillMessage(
            publisher_name="consumer-registration",
            ts=datetime.now(),
            realms_topics=subscriber.realms_topics,
            subscriber_name=subscriber.name,
        )
        await self._port.add_message("prefill", message)

    async def get_realm_topic_subscribers(self, realm_topic: str) -> List[str]:
        return await self.get_subscriber_names(realm_topic)
