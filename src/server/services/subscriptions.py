# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Optional

from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext

from univention.provisioning.models import (
    DISPATCHER_SUBJECT_TEMPLATE,
    PREFILL_SUBJECT_TEMPLATE,
    REALM_TOPIC_PREFIX,
    Bucket,
    FillQueueStatus,
    NewSubscription,
    Subscription,
)

from .port import Port

REALM_TOPIC_TEMPLATE = "{realm}:{topic}"
logger = logging.getLogger(__name__)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SubscriptionService:
    def __init__(self, port: Port):
        self._port = port

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

    async def is_subscriptions_matching(self, new_sub: NewSubscription, existing_sub: Subscription) -> bool:
        if existing_sub.request_prefill != new_sub.request_prefill:
            return False

        hashed_password = await self._port.get_str_value(new_sub.name, Bucket.credentials)
        valid = password_context.verify(new_sub.password, hashed_password)
        if not valid:
            return False

        new_realms_topics = [REALM_TOPIC_TEMPLATE.format(realm=r, topic=t) for r, t in new_sub.realms_topics]
        if new_realms_topics != existing_sub.realms_topics:
            return False

        return True

    async def register_subscription(self, new_sub: NewSubscription) -> bool:
        """Register a new subscription."""

        existing_sub = await self.get_subscription_info(new_sub.name)
        if existing_sub:
            if not await self.is_subscriptions_matching(new_sub, existing_sub):
                raise HTTPException(
                    status_code=409,
                    detail="Subscription with the given name already registered but with different parameters.",
                )
            return False
        else:
            logger.info("Registering new subscription with the name: %s", new_sub.name)
            encrypted_password = self.hash_password(new_sub.password)
            await self._port.put_value(new_sub.name, encrypted_password, Bucket.credentials)
            await self.prepare_and_store_subscription_info(new_sub)
            logger.info("New subscription was registered")
            return True

    async def prepare_and_store_subscription_info(self, new_sub: NewSubscription):
        if new_sub.request_prefill:
            prefill_queue_status = FillQueueStatus.pending
        else:
            prefill_queue_status = FillQueueStatus.done

        realms_topics_str = [REALM_TOPIC_TEMPLATE.format(realm=r, topic=t) for r, t in new_sub.realms_topics]
        sub_info = Subscription(
            name=new_sub.name,
            realms_topics=realms_topics_str,
            request_prefill=new_sub.request_prefill,
            prefill_queue_status=prefill_queue_status,
        )
        await self.set_sub_info(new_sub.name, sub_info)
        await self.update_realm_topic_subscriptions(sub_info.realms_topics, new_sub.name)
        await self._port.ensure_stream(
            new_sub.name,
            True,
            [
                DISPATCHER_SUBJECT_TEMPLATE.format(subscription=new_sub.name),
                PREFILL_SUBJECT_TEMPLATE.format(subscription=new_sub.name),
            ],
        )
        await self._port.ensure_consumer(new_sub.name)

    async def update_realm_topic_subscriptions(self, realms_topics: List[str], name: str):
        for realm_topic in realms_topics:
            realm_topic_key = f"{REALM_TOPIC_PREFIX}.{realm_topic}"
            subs = await self._port.get_list_value(realm_topic_key, Bucket.subscriptions)
            subs.append(name)
            await self._port.put_value(realm_topic_key, subs, Bucket.subscriptions)

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

        await self._port.delete_kv_pair(name, Bucket.credentials)
        await self.delete_sub_info(name)
        await self._port.delete_stream(name)
        await self._port.delete_consumer(name)

    async def delete_sub_from_realm_topic(self, realm_topic_str: str, name: str):
        logger.debug("Deleting subscription %s from %s", name, realm_topic_str)
        realm_topic_key = f"{REALM_TOPIC_PREFIX}.{realm_topic_str}"
        subs = await self._port.get_list_value(realm_topic_key, Bucket.subscriptions)
        if not subs:
            raise ValueError("There are no subscriptions")

        if name not in subs:
            raise ValueError("The subscription with the given name does not exist")

        subs.remove(name)
        await self._port.put_value(realm_topic_key, subs, Bucket.subscriptions)

        logger.info("Subscription was deleted")

    async def delete_sub_info(self, name: str):
        await self._port.delete_kv_pair(name, Bucket.subscriptions)

    def handle_authentication_error(self, message: str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Basic"},
        )

    async def authenticate_user(self, credentials: HTTPBasicCredentials, subscription_name: Optional[str] = None):
        if subscription_name and subscription_name != credentials.username:
            self.handle_authentication_error("You do not have access to this data")

        hashed_password = await self._port.get_str_value(credentials.username, Bucket.credentials)

        valid, new_hash = password_context.verify_and_update(credentials.password, hashed_password)
        if valid:
            if new_hash:
                logger.info("Storing new password hash for user %r.", credentials.username)
                await self._port.put_value(credentials.username, new_hash, Bucket.credentials)
        else:
            self.handle_authentication_error("Incorrect username or password")
