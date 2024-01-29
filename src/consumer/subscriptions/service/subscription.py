# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
import re
from datetime import datetime
from typing import List, Optional

from consumer.port import ConsumerPort
from consumer.subscriptions.subscription.sink import SinkManager
from shared.models import Subscription, NewSubscription, FillQueueStatus
from shared.models.queue import PrefillMessage

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
    subscriptions = "subscriptions"

    def subscription(subscription_name: str) -> str:
        return f"subscription:{subscription_name}"


class SubscriptionService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def get_subscriptions(
        self, realm_topic: Optional[None]
    ) -> List[Subscription]:
        """
        Return a list of all known subscriptions or with the given realm_topic.
        """

        names = await self.get_subscription_names(
            realm_topic or SubscriptionKeys.subscriptions
        )
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
            raise ValueError("Subscription not found.")

        return sub

    async def create_subscription(self, sub: NewSubscription):
        """
        Create a new subscription.
        """
        if sub.request_prefill:
            prefill_queue_status = FillQueueStatus.pending
        else:
            prefill_queue_status = FillQueueStatus.done

        sub_info = await self.get_subscription_info(sub.name)
        if sub_info:
            raise ValueError("The subscription with the given name already exists")
        else:
            sub_info = Subscription(
                name=sub.name,
                realm=sub.realm,
                topic=sub.topic,
                request_prefill=sub.request_prefill,
                prefill_queue_status=prefill_queue_status,
            )
            await self.set_sub_info(sub.name, sub_info)
            await self.add_sub_to_subscriptions(sub.name)
            await self.update_realm_topic_subscriptions(
                f"{sub.realm}:{sub.topic}", sub.name
            )
            await self._port.create_stream(sub.name)
            await self._port.create_consumer(sub.name)

            self.logger.info("Subscription was created")

    async def update_realm_topic_subscriptions(self, realm_topic_str: str, name: str):
        await self.update_subscriptions_names(realm_topic_str, name)

    async def get_subscription_info(self, name: str) -> Optional[Subscription]:
        result = await self._port.get_dict_value(SubscriptionKeys.subscription(name))
        return Subscription.model_validate(result) if result else result

    async def get_subscription_queue_status(self, name: str) -> FillQueueStatus:
        """Get the pre-fill status of the given subscription."""

        sub_info = await self.get_subscription_info(name)
        if not sub_info:
            raise ValueError("Subscription not found.")

        return sub_info.prefill_queue_status

    async def set_subscription_queue_status(self, name: str, status: FillQueueStatus):
        """Set the pre-fill status of the given subscription."""
        sub_info = await self.get_subscription_info(name)
        if not sub_info:
            raise ValueError("Subscription not found.")

        sub_info.prefill_queue_status = status.name
        await self.set_sub_info(name, sub_info)

    async def cancel_subscription(self, name: str, realm: str, topic: str):
        sub_info = await self.get_subscription_info(name)
        if not sub_info:
            raise ValueError("Subscription not found.")

        await self.delete_sub_from_realm_topic(f"{realm}:{topic}", name)
        await self.delete_sub_info(name)
        await self.delete_sub_from_subscriptions(name)
        await self._port.delete_stream(name)
        await self._port.delete_consumer(name)

    async def set_sub_info(self, name, sub_info: Subscription):
        await self._port.put_value(
            SubscriptionKeys.subscription(name), sub_info.model_dump()
        )

    async def delete_sub_from_subscriptions(self, name: str):
        await self.delete_subscription_from_values(SubscriptionKeys.subscriptions, name)

    async def delete_sub_from_realm_topic(self, realm_topic_str: str, name: str):
        await self.delete_subscription_from_values(realm_topic_str, name)

    async def delete_sub_info(self, name: str):
        await self._port.delete_kv_pair(SubscriptionKeys.subscription(name))

    async def delete_subscription_from_values(self, key: str, name: str):
        self.logger.debug("Deleting subscription '%s' from '%s'", name, key)

        subs = await self._port.get_list_value(key)
        if not subs:
            raise ValueError("There are no subscriptions")

        if name not in subs:
            raise ValueError("The subscription with the given name does not exist")

        subs.remove(name)
        await self._port.put_list_value(key, subs)

        self.logger.info("Subscription was deleted")

    async def update_subscriptions_names(self, key: str, value: str) -> None:
        subs = await self._port.get_str_value(key)
        if subs:
            value = subs + f",{value}"
        await self._port.put_value(key, value)

    async def add_sub_to_subscriptions(self, name: str):
        await self.update_subscriptions_names(SubscriptionKeys.subscriptions, name)

    async def send_request_to_prefill(self, subscriber: NewSubscription):
        self.logger.info("Sending the request to prefill")
        message = PrefillMessage(
            publisher_name="consumer-registration",
            ts=datetime.now(),
            realm=subscriber.realm,
            topic=subscriber.topic,
            subscription_name=subscriber.name,
        )
        await self._port.add_message("prefill", message)
