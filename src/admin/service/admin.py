# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from passlib.context import CryptContext

from admin.port import AdminPort

from shared.models import FillQueueStatus, PrefillMessage, Subscription, NewSubscription
from shared.models.subscription import Bucket

REALM_TOPIC_TEMPLATE = "{realm}:{topic}"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AdminService:
    def __init__(self, port: AdminPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

    async def get_subscriptions(self) -> List[Subscription]:
        """
        Return a list of all known subscriptions.
        """

        names = await self.get_subscription_names()
        subscriptions = [await self.get_subscription_info(name) for name in names]

        return subscriptions

    async def get_subscription_names(self):
        return await self._port.get_bucket_keys(Bucket.credentials)

    @staticmethod
    def get_hashed_password(password: str) -> str:
        return password_context.hash(password)

    async def register_subscription(self, new_sub: NewSubscription):
        """Register a new subscription."""

        if await self._port.get_str_value(new_sub.name, Bucket.credentials):
            raise HTTPException(
                status_code=400,
                detail="Subscription with the given name already registered",
            )
        else:
            self.logger.info(
                "Registering new subscription with the name: %s", new_sub.name
            )
            encrypted_password = self.get_hashed_password(new_sub.password)
            await self._port.put_value(
                new_sub.name, encrypted_password, Bucket.credentials
            )

            await self.prepare_and_store_subscription_info(new_sub)

            self.logger.info("New subscription was registered")

    async def prepare_and_store_subscription_info(self, new_sub: NewSubscription):
        if new_sub.request_prefill:
            prefill_queue_status = FillQueueStatus.pending
        else:
            prefill_queue_status = FillQueueStatus.done

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
        await self.update_realm_topic_subscriptions(
            sub_info.realms_topics, new_sub.name
        )
        await self._port.create_stream(new_sub.name)
        await self._port.create_consumer(new_sub.name)

    async def update_realm_topic_subscriptions(
        self, realms_topics: List[str], name: str
    ):
        for realm_topic in realms_topics:
            await self.update_subscription_names(realm_topic, name)

    async def set_sub_info(self, name, sub_info: Subscription):
        await self._port.put_value(name, sub_info.model_dump(), Bucket.subscriptions)

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
