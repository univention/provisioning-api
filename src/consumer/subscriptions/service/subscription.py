# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
import re
from datetime import datetime
from typing import List, Optional

from consumer.port import ConsumerPort
from consumer.subscriptions.subscription.sink import SinkManager
from shared.models import Subscription, NewSubscription, FillQueueStatus, PrefillMessage

manager = SinkManager()
SUBSCRIPTIONS = "subscriptions"
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

    async def get_subscriptions(self) -> List[Subscription]:
        """
        Return a list of all known subscriptions.
        """

        names = await self.get_subscription_names(SUBSCRIPTIONS)
        subscriptions = [await self.get_subscription(name) for name in names]

        return subscriptions

    async def get_subscription_names(self, key: str):
        return await self._port.get_list_value(key)

    async def get_subscription(self, name: str) -> Subscription:
        """
        Get information about a registered subscription.
        """
        sub = await self.get_subscription_info(name)
        if not sub:
            raise ValueError("Subscription was not found.")

        return sub

    async def create_subscription(self, new_sub: NewSubscription):
        """
        Add a new subscription.
        """
        if new_sub.request_prefill:
            prefill_queue_status = FillQueueStatus.pending
        else:
            prefill_queue_status = FillQueueStatus.done

        sub_info = await self.get_subscription_info(new_sub.name)
        if sub_info:
            raise ValueError("Subscription with the given name already exists")

        else:
            self.logger.debug(
                "Creating new subscription with the name: %s", new_sub.name
            )
            realms_topics_str = [
                REALM_TOPIC_TEMPLATE.format(realm=r, topic=t)
                for r, t in new_sub.realms_topics
            ]
            sub_info = Subscription(
                name=new_sub.name,
                realms_topics=realms_topics_str,
                request_prefill=new_sub.request_prefill,
                prefill_queue_status=prefill_queue_status,
            )
            await self.set_sub_info(new_sub.name, sub_info)
            await self.add_sub_to_subscriptions(new_sub.name)
            await self.update_realm_topic_subscriptions(
                sub_info.realms_topics, new_sub.name
            )
            await self._port.create_stream(new_sub.name)
            await self._port.create_consumer(new_sub.name)

            self.logger.info("New subscriber was created")

    async def update_realm_topic_subscriptions(
        self, realms_topics: List[str], name: str
    ):
        for realm_topic in realms_topics:
            await self.update_subscription_names(realm_topic, name)

    async def get_subscription_info(self, name: str) -> Optional[Subscription]:
        result = await self._port.get_dict_value(name)
        return Subscription.model_validate(result) if result else result

    async def get_subscription_queue_status(self, name: str) -> FillQueueStatus:
        """Get the pre-fill status of the given subscription."""

        sub_info = await self.get_subscription_info(name)
        if not sub_info:
            raise ValueError("Subscription was not found.")

        return sub_info.prefill_queue_status

    async def set_subscription_queue_status(self, name: str, status: FillQueueStatus):
        """Set the pre-fill status of the given subscription."""

        sub_info = await self.get_subscription_info(name)
        if not sub_info:
            raise ValueError("Subscription was not found.")

        sub_info.prefill_queue_status = status.name
        await self.set_sub_info(name, sub_info)

    async def set_sub_info(self, name, sub_info: Subscription):
        await self._port.put_value(name, sub_info.model_dump())

    async def delete_subscription(self, name: str):
        """
        Delete a subscription and all of its data.
        """

        sub_info = await self.get_subscription_info(name)
        if not sub_info:
            raise ValueError("Subscription was not found.")

        for realm_topic in sub_info.realms_topics:
            await self.delete_sub_from_realm_topic(realm_topic, name)

        await self.delete_sub_from_subscriptions(name)
        await self.delete_sub_info(name)
        await self._port.delete_stream(name)
        await self._port.delete_consumer(name)

    async def delete_sub_from_subscriptions(self, name: str):
        await self.delete_subscription_from_values(SUBSCRIPTIONS, name)

    async def delete_sub_from_realm_topic(self, realm_topic_str: str, name: str):
        await self.delete_subscription_from_values(realm_topic_str, name)

    async def delete_sub_info(self, name: str):
        await self._port.delete_kv_pair(name)

    async def delete_subscription_from_values(self, key: str, name: str):
        self.logger.debug("Deleting subscription %s from %s", name, key)

        subs = await self._port.get_list_value(key)
        if not subs:
            raise ValueError("There are no subscriptions")

        if name not in subs:
            raise ValueError("The subscription with the given name does not exist")

        subs.remove(name)
        await self._port.put_list_value(key, subs)

        self.logger.info("Subscription was deleted")

    async def update_subscription_names(self, key: str, value: str) -> None:
        subs = await self._port.get_str_value(key)
        if subs:
            value = subs + f",{value}"
        await self._port.put_value(key, value)

    async def add_sub_to_subscriptions(self, name: str):
        await self.update_subscription_names(SUBSCRIPTIONS, name)

    async def send_request_to_prefill(self, subscriber: NewSubscription):
        self.logger.info("Sending the requests to prefill")
        message = PrefillMessage(
            publisher_name="consumer-registration",
            ts=datetime.now(),
            realms_topics=subscriber.realms_topics,
            subscription_name=subscriber.name,
        )
        await self._port.add_message("prefill", message)

    async def get_realm_topic_subscriptions(self, realm_topic: str) -> List[str]:
        return await self.get_subscription_names(realm_topic)
