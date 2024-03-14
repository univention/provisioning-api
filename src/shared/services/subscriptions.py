# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Optional

from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext

from .port import Port
from shared.models import Subscription, FillQueueStatus, NewSubscription
from shared.models.subscription import Bucket

REALM_TOPIC_TEMPLATE = "{realm}:{topic}"
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SubscriptionService:
    def __init__(self, port: Port):
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
    def hash_password(password: str) -> str:
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
            encrypted_password = self.hash_password(new_sub.password)
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

    async def update_subscription_names(self, key: str, value: str) -> None:
        subs = await self._port.get_list_value(key, Bucket.subscriptions)
        subs.append(value)
        await self._port.put_value(key, subs, Bucket.subscriptions)

    async def get_subscription(self, name: str) -> Subscription:
        """
        Get information about a registered subscription.
        """
        sub = await self.get_subscription_info(name)
        if not sub:
            raise ValueError("Subscription was not found.")

        return sub

    async def get_subscription_info(self, name: str) -> Optional[Subscription]:
        result = await self._port.get_dict_value(name, Bucket.subscriptions)
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
        await self._port.put_value(name, sub_info.model_dump(), Bucket.subscriptions)

    async def delete_subscription(self, name: str):
        """
        Delete a subscription and all of its data.
        """

        sub_info = await self.get_subscription_info(name)
        if not sub_info:
            raise ValueError("Subscription was not found.")

        for realm_topic in sub_info.realms_topics:
            await self.delete_sub_from_realm_topic(realm_topic, name)

        # FIXME: who is responsible for deleting subscription's credentials from the store?
        await self._port.delete_kv_pair(name, Bucket.credentials)
        await self.delete_sub_info(name)
        await self._port.delete_stream(name)
        await self._port.delete_consumer(name)

    async def delete_sub_from_realm_topic(self, realm_topic_str: str, name: str):
        await self.delete_subscription_from_values(realm_topic_str, name)

    async def delete_sub_info(self, name: str):
        await self._port.delete_kv_pair(name, Bucket.subscriptions)

    async def delete_subscription_from_values(self, key: str, name: str):
        self.logger.debug("Deleting subscription %s from %s", name, key)

        subs = await self._port.get_list_value(key, Bucket.subscriptions)
        if not subs:
            raise ValueError("There are no subscriptions")

        if name not in subs:
            raise ValueError("The subscription with the given name does not exist")

        subs.remove(name)
        await self._port.put_value(key, subs, Bucket.subscriptions)

        self.logger.info("Subscription was deleted")

    async def get_realm_topic_subscriptions(self, realm_topic: str) -> List[str]:
        return await self._port.get_list_value(realm_topic, Bucket.subscriptions)

    def handle_authentication_error(self, message: str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Basic"},
        )

    async def authenticate_user(
        self, credentials: HTTPBasicCredentials, subscription_name: Optional[str] = None
    ):
        if subscription_name and subscription_name != credentials.username:
            self.handle_authentication_error("You do not have access to this data")

        hashed_password = await self._port.get_str_value(
            credentials.username, Bucket.credentials
        )

        valid, new_hash = password_context.verify_and_update(
            credentials.password, hashed_password
        )
        if valid:
            if new_hash:
                await self._port.put_value(
                    credentials.username, new_hash, Bucket.credentials
                )
        else:
            self.handle_authentication_error("Incorrect username or password")
