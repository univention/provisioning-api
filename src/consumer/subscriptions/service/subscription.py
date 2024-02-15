# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
import re
from typing import List, Optional

from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials
from passlib.context import CryptContext

from consumer.port import ConsumerPort
from consumer.subscriptions.subscription.sink import SinkManager
from shared.models import Subscription, FillQueueStatus
from shared.models.subscription import Bucket

manager = SinkManager()
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


class SubscriptionService:
    def __init__(self, port: ConsumerPort):
        self._port = port
        self.logger = logging.getLogger(__name__)

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
        await self._port.put_list_value(key, subs, Bucket.subscriptions)

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
        if hashed_password is None or not verify_password(
            credentials.password, hashed_password
        ):
            self.handle_authentication_error("Incorrect username or password")
