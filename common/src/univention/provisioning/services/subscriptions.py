# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Optional

import cachetools.func
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext

from univention.provisioning.models.constants import DISPATCHER_SUBJECT_TEMPLATE, PREFILL_SUBJECT_TEMPLATE, Bucket
from univention.provisioning.models.subscription import FillQueueStatus, Subscription
from univention.provisioning.rest.models import NewSubscription

from .port import Port

REALM_TOPIC_TEMPLATE = "{realm}:{topic}"
logger = logging.getLogger(__name__)
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
PASSWORD_CACHE_TTL = 30.0


@cachetools.func.ttl_cache(maxsize=32, ttl=PASSWORD_CACHE_TTL)
def verify_and_update_password(
    cleartext_pw: str, hashed_pw: str, subscription_name: Optional[str] = None
) -> tuple[bool, str | None]:
    """
    Caching wrapper around CryptContext.verify_and_update()

    Caches all hits and exceptions!
    But the caller (SubscriptionService.authenticate_user()) will delete negative hits, so we cache only positive hits.
    """
    return password_context.verify_and_update(cleartext_pw, hashed_pw)  # takes ~200ms


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
        """
        Determine if `new_sub` and `existing_sub` have the same values in their common fields
        (ignoring `prefill_queue_status` and `password`).
        """
        if existing_sub.request_prefill != new_sub.request_prefill:
            return False

        if new_sub.realms_topics != existing_sub.realms_topics:
            return False

        hashed_password = await self._port.get_str_value(new_sub.name, Bucket.credentials)
        valid = password_context.verify(new_sub.password, hashed_password)
        if not valid:
            return False

        return True

    async def register_subscription(self, new_sub: NewSubscription) -> bool:
        """Register a new subscription."""

        existing_sub = await self.get_subscription_info(new_sub.name)
        if existing_sub:
            if not await self.is_subscriptions_matching(new_sub, existing_sub):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Subscription with the given name already registered but with different parameters.",
                )
            return False
        else:
            logger.info(
                "Registering new subscription (name: %r realms_topics: %r request_prefill: %r).",
                new_sub.name,
                new_sub.realms_topics,
                new_sub.request_prefill,
            )
            encrypted_password = self.hash_password(new_sub.password)
            await self._port.put_value(new_sub.name, encrypted_password, Bucket.credentials)
            await self.prepare_and_store_subscription_info(new_sub)
            logger.info("New subscription was registered: %r", new_sub.name)
            return True

    async def prepare_and_store_subscription_info(self, new_sub: NewSubscription):
        if new_sub.request_prefill:
            prefill_queue_status = FillQueueStatus.pending
        else:
            prefill_queue_status = FillQueueStatus.done

        sub_info = Subscription(
            name=new_sub.name,
            realms_topics=new_sub.realms_topics,
            request_prefill=new_sub.request_prefill,
            prefill_queue_status=prefill_queue_status,
        )
        await self.set_sub_info(new_sub.name, sub_info)
        await self._port.ensure_stream(
            new_sub.name,
            True,
            [
                DISPATCHER_SUBJECT_TEMPLATE.format(subscription=new_sub.name),
                PREFILL_SUBJECT_TEMPLATE.format(subscription=new_sub.name),
            ],
        )
        await self._port.ensure_consumer(new_sub.name)

    async def get_subscription(self, name: str) -> Subscription:
        """
        Get information about a registered subscription.
        """
        if sub := await self.get_subscription_info(name):
            return sub
        else:
            raise ValueError("Subscription was not found.")

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

        await self._port.delete_kv_pair(name, Bucket.credentials)
        await self.delete_sub_info(name)
        await self._port.delete_stream(name)
        await self._port.delete_consumer(name)

    async def delete_sub_info(self, name: str):
        await self._port.delete_kv_pair(name, Bucket.subscriptions)

    @staticmethod
    def handle_authentication_error(message: str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=message,
            headers={"WWW-Authenticate": "Basic"},
        )

    async def authenticate_user(self, credentials: HTTPBasicCredentials, subscription_name: Optional[str] = None):
        if subscription_name and subscription_name != credentials.username:
            self.handle_authentication_error("You do not have access to this data")

        hashed_password = await self._port.get_str_value(credentials.username, Bucket.credentials)
        cached_func_args = (credentials.password, hashed_password, subscription_name)
        valid, new_hash = verify_and_update_password(*cached_func_args)
        if valid:
            if new_hash:
                logger.info("Storing new password hash for user %r.", credentials.username)
                await self._port.put_value(credentials.username, new_hash, Bucket.credentials)
        else:
            # cache only positive authentication attempts -> remove cache entry for invalid password
            cache_key = verify_and_update_password.cache_key(*cached_func_args)
            verify_and_update_password.cache.pop(cache_key, None)
            self.handle_authentication_error("Incorrect username or password")
