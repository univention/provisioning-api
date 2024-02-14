# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from typing import List, Optional

from admin.port import AdminPort

from shared.models import FillQueueStatus, PrefillMessage, Subscription, NewSubscription
from shared.models.subscription import Bucket

REALM_TOPIC_TEMPLATE = "{realm}:{topic}"
SUBSCRIPTIONS = "subscriptions"


class AdminService:
    def __init__(self, port: AdminPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def get_subscriptions(self) -> List[Subscription]:
        """
        Return a list of all known subscriptions.
        """

        names = await self.get_subscription_names(SUBSCRIPTIONS)
        subscriptions = [await self.get_subscription_info(name) for name in names]

        return subscriptions

    async def get_subscription_names(self, key: str):
        # FIXME: get a list of all known subscriptions using CREDENTIALS bucket
        return await self._port.get_list_value(key, Bucket.subscriptions)

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

            self.logger.info("New subscription was created")

    async def update_realm_topic_subscriptions(
        self, realms_topics: List[str], name: str
    ):
        for realm_topic in realms_topics:
            await self.update_subscription_names(realm_topic, name)

    async def set_sub_info(self, name, sub_info: Subscription):
        await self._port.put_value(name, sub_info.model_dump(), Bucket.subscriptions)

    async def add_sub_to_subscriptions(self, name: str):
        await self.update_subscription_names(SUBSCRIPTIONS, name)

    async def update_subscription_names(self, key: str, value: str) -> None:
        subs = await self._port.get_str_value(key, Bucket.subscriptions)
        if subs:
            value = subs + f",{value}"
        await self._port.put_value(key, value, Bucket.subscriptions)

    async def send_request_to_prefill(self, subscription: NewSubscription):
        self.logger.info("Sending the requests to prefill")
        message = PrefillMessage(
            publisher_name="consumer-registration",
            ts=datetime.now(),
            realms_topics=subscription.realms_topics,
            subscription_name=subscription.name,
        )
        await self._port.add_message("prefill", message)

    async def get_subscription_info(self, name: str) -> Optional[Subscription]:
        result = await self._port.get_dict_value(name, Bucket.subscriptions)
        return Subscription.model_validate(result) if result else result
