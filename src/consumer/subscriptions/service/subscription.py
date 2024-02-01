# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import base64
import logging
import re
from datetime import datetime
from typing import List, Optional, Union

from consumer.port import ConsumerPort
from consumer.subscriptions.subscription.sink import SinkManager
from shared.models import Subscription, NewSubscription, FillQueueStatus
from shared.models.queue import PrefillMessage
from shared.models.subscription import Subscriber

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

    def subscription(subscription_name: str) -> str:
        return f"subscription:{subscription_name}"


class SubscriptionService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def get_subscribers(self) -> List[Union[Subscriber, str]]:
        """
        Return a list of all known subscribers.
        """

        names = await self.get_subscribers_names(SubscriptionKeys.subscribers)
        subscriptions = [await self.get_subscriber_info(name) for name in names]
        return subscriptions

    async def get_realm_topic_subscribers(self, realm_topic: Optional[str]):
        if not realm_topic:
            return []

        names = await self.get_subscribers_names(SubscriptionKeys.subscribers)
        encoded_realm_topic = base64.b64encode(realm_topic.encode()).decode()

        subscription_infos = await asyncio.gather(
            *[self.get_subscription_info(encoded_realm_topic, name) for name in names]
        )

        subscribers = [
            name
            for name, subscription_info in zip(names, subscription_infos)
            if subscription_info
        ]
        return subscribers

    async def get_subscribers_names(self, key: str):
        return await self._port.get_list_value(key, "main")

    async def create_subscription(self, new_sub: NewSubscription):
        """
        Create a new subscription.
        """
        if new_sub.request_prefill:
            prefill_queue_status = FillQueueStatus.pending
        else:
            prefill_queue_status = FillQueueStatus.done

        encoded_realm_topic = base64.b64encode(
            f"{new_sub.realm}:{new_sub.topic}".encode()
        ).decode()

        if not await self._port.subscriber_exists(new_sub.name):
            await self._port.create_subscriber(new_sub.name)
            await self.add_sub_to_subscribers(new_sub.name)

        if await self.get_subscription_info(encoded_realm_topic, new_sub.name):
            raise ValueError(
                "The subscription with the given realm_topic already exists"
            )
        else:
            sub_info = Subscription(
                realm=new_sub.realm,
                topic=new_sub.topic,
                request_prefill=new_sub.request_prefill,
                prefill_queue_status=prefill_queue_status,
            )
            await self.set_sub_info(sub_info, bucket=new_sub.name)

            encoded_realm_topic = base64.b64encode(
                f"{new_sub.realm}:{new_sub.topic}".encode()
            ).decode()
            await self._port.create_stream(f"{new_sub.name}_{encoded_realm_topic}")
            await self._port.create_consumer(f"{new_sub.name}_{encoded_realm_topic}")

            self.logger.info("Subscription was created")

    async def update_realm_topic_subscriptions(self, realm_topic_str: str, name: str):
        await self.update_subscribers_names(realm_topic_str, name)

    async def get_subscription_names(self, subscriber_name: str):
        return await self._port.get_subscription_names(subscriber_name)

    async def get_subscriber_info(self, subscriber_name: str) -> Optional[Subscriber]:
        if not await self._port.subscriber_exists(subscriber_name):
            raise ValueError("Subscriber was not found.")

        names = await self.get_subscription_names(subscriber_name)
        subscriptions = [
            await self.get_subscription_info(name, subscriber_name) for name in names
        ]

        sub = Subscriber(name=subscriber_name, subscriptions=subscriptions)
        return sub

    async def get_subscription_info(self, key: str, bucket: str) -> Subscription:
        result = await self._port.get_dict_value(key, bucket)
        return Subscription.model_validate(result) if result else result

    async def get_subscription_queue_status(self, name: str) -> FillQueueStatus:
        """Get the pre-fill status of the given subscription."""
        bucket, key = name.split("_")
        sub_info = await self.get_subscription_info(key, bucket)
        if not sub_info:
            raise ValueError("Subscription was not found.")

        return sub_info.prefill_queue_status

    async def set_subscription_queue_status(
        self, name: str, realm_topic: str, status: FillQueueStatus
    ):
        """Set the pre-fill status of the given subscription."""
        encoded_realm_topic = base64.b64encode(realm_topic.encode()).decode()
        sub_info = await self.get_subscription_info(encoded_realm_topic, name)
        if not sub_info:
            raise ValueError("Subscription was not found.")

        sub_info.prefill_queue_status = status.name
        await self.set_sub_info(sub_info, bucket=name)

    async def cancel_subscription(self, name: str, realm_topic: str):
        encoded_realm_topic = base64.b64encode(realm_topic.encode()).decode()
        sub_info = await self.get_subscription_info(encoded_realm_topic, name)
        if not sub_info:
            raise ValueError("Subscription was not found.")

        await self.delete_sub_info(encoded_realm_topic, name)
        await self._port.delete_stream(f"{name}_{encoded_realm_topic}")
        await self._port.delete_consumer(f"{name}_{encoded_realm_topic}")

    async def set_sub_info(self, sub_info: Subscription, bucket: str):
        encoded_realm_topic = base64.b64encode(
            f"{sub_info.realm}:{sub_info.topic}".encode()
        ).decode()

        await self._port.put_value(
            encoded_realm_topic, sub_info.model_dump(), bucket=bucket
        )

    async def delete_subscriber(self, name: str):
        await self.delete_subscriber_from_values(SubscriptionKeys.subscribers, name)
        await self._port.delete_subscriber(name)
        self.logger.info("Subscriber was deleted")

    async def delete_sub_info(self, key: str, bucket: str):
        await self._port.delete_kv_pair(key, bucket)

    async def delete_subscriber_from_values(self, key: str, name: str):
        self.logger.debug("Deleting subscriber '%s' from '%s'", name, key)

        subs = await self._port.get_list_value(key, "main")
        if name not in subs:
            raise ValueError("Subscriber was not found")

        subs.remove(name)
        await self._port.put_list_value(key, subs, "main")

    async def update_subscribers_names(self, key: str, value: str) -> None:
        subs = await self._port.get_str_value(key, "main")
        if subs:
            value = subs + f",{value}"
        await self._port.put_value(key, value, bucket="main")

    async def add_sub_to_subscribers(self, name: str):
        await self.update_subscribers_names(SubscriptionKeys.subscribers, name)

    async def send_request_to_prefill(self, subscriber: NewSubscription):
        self.logger.info("Sending the request to prefill")
        message = PrefillMessage(
            publisher_name="consumer-registration",
            ts=datetime.now(),
            realm=subscriber.realm,
            topic=subscriber.topic,
            subscriber_name=subscriber.name,
        )
        await self._port.add_message("prefill", message)
