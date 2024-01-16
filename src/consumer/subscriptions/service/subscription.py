# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
import re
from typing import List, Optional

from consumer.port import ConsumerPort
from consumer.subscriptions.subscription.sink import SinkManager
from shared.models import Subscriber, NewSubscriber, FillQueueStatus

manager = SinkManager()


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


class SubscriptionKeys:
    subscribers = "subscribers"

    def subscriber(subscriber_name: str) -> str:
        return f"subscriber:{subscriber_name}"


class SubscriptionService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def get_subscribers(self, realm_topic: Optional[None]) -> List[Subscriber]:
        """
        Return a list of all known subscribers or with the given realm_topic.
        """

        names = await self.get_subscriber_names(
            realm_topic or SubscriptionKeys.subscribers
        )
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

    async def create_subscription(self, sub: NewSubscriber):
        """
        Add a new subscription.
        """
        if sub.fill_queue:
            fill_queue_status = FillQueueStatus.pending
        else:
            fill_queue_status = FillQueueStatus.done

        realm_topic_str = f"{sub.realm_topic[0]}:{sub.realm_topic[1]}"
        sub_info = await self.get_subscriber_info(sub.name)
        if sub_info:
            if realm_topic_str in sub_info.realms_topics:
                raise ValueError(
                    "Subscription for the given realm_topic already exists"
                )

            self.logger.debug(
                "Creating subscription for the realm_topic: %s", realm_topic_str
            )
            sub_info.realms_topics.append(realm_topic_str)
            await self.set_sub_info(sub.name, sub_info)
            await self.update_realm_topic_subscribers(realm_topic_str, sub.name)

            self.logger.info("Subscription was created")
        else:
            await self.add_subscriber(sub, fill_queue_status, realm_topic_str)

    async def update_realm_topic_subscribers(self, realm_topic_str: str, name: str):
        await self.update_subscriber_names(realm_topic_str, name)

    async def add_subscriber(
        self,
        sub: NewSubscriber,
        fill_queue_status: FillQueueStatus,
        realm_topic_str: str,
    ):
        self.logger.debug("Creating new subscriber with the name: %s", sub.name)
        sub_info = Subscriber(
            name=sub.name,
            realms_topics=[f"{sub.realm_topic[0]}:{sub.realm_topic[1]}"],
            fill_queue=sub.fill_queue,
            fill_queue_status=fill_queue_status,
        )
        await self.set_sub_info(sub.name, sub_info)
        await self.add_sub_to_subscribers(sub.name)
        await self.update_realm_topic_subscribers(realm_topic_str, sub.name)

        self.logger.info("New subscriber was created")

    async def get_subscriber_info(self, name: str) -> Optional[Subscriber]:
        result = await self._port.get_dict_value(SubscriptionKeys.subscriber(name))
        return Subscriber.model_validate(result) if result else result

    async def get_subscriber_queue_status(self, name: str) -> FillQueueStatus:
        """Get the pre-fill status of the given subscriber."""

        sub_info = await self.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber not found.")

        return sub_info.fill_queue_status

    async def set_subscriber_queue_status(self, name: str, status: FillQueueStatus):
        """Set the pre-fill status of the given subscriber."""
        sub_info = await self.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber not found.")

        sub_info.fill_queue_status = status.name
        await self.set_sub_info(name, sub_info)

    async def cancel_subscription(self, name: str, realm_topic: str):
        sub_info = await self.get_subscriber_info(name)
        if not sub_info:
            raise ValueError("Subscriber not found.")

        realms_topics = sub_info.realms_topics
        if realm_topic not in realms_topics:
            raise ValueError("Subscription for the given realm_topic doesn't exist")

        realms_topics.remove(realm_topic)
        await self.delete_sub_from_realm_topic(realm_topic, name)
        await self.set_sub_info(name, sub_info)

    async def set_sub_info(self, name, sub_info: Subscriber):
        await self._port.put_value(
            SubscriptionKeys.subscriber(name), sub_info.model_dump()
        )

    async def delete_subscriber(self, name: str):
        """
        Delete a subscriber and all of its data.
        """
        await manager.close(name)

        sub_info = await self.get_subscriber_info(name)
        if sub_info:
            for realm_topic in sub_info.realms_topics:
                await self.delete_sub_from_realm_topic(realm_topic, name)

        await self.delete_sub_from_subscribers(name)
        await self.delete_sub_info(SubscriptionKeys.subscriber(name))
        await self._port.delete_queue(name)

    async def delete_sub_from_subscribers(self, name: str):
        await self.delete_subscriber_from_values(SubscriptionKeys.subscribers, name)

    async def delete_sub_from_realm_topic(self, realm_topic_str: str, name: str):
        await self.delete_subscriber_from_values(realm_topic_str, name)

    async def delete_sub_info(self, name: str):
        await self._port.delete_kv_pair(SubscriptionKeys.subscriber(name))

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
        await self.update_subscriber_names(SubscriptionKeys.subscribers, name)
