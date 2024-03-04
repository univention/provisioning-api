# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional

import aiohttp

from admin.config import admin_settings
from shared.models import (
    Subscription,
    ProvisioningMessage,
    MessageProcessingStatusReport,
    Event,
    NewSubscription,
    MessageProcessingStatus,
)

from shared.models.queue import Message

from shared.client.config import ClientSettings

logger = logging.getLogger(__file__)


class AsyncClient:
    def __init__(self, settings: Optional[ClientSettings] = None) -> None:
        self.settings = settings or ClientSettings()

    async def create_subscription(self):
        logger.info("creating subscription for %s", str(self.settings.realms_topics))
        subscription = NewSubscription(
            name=self.settings.consumer_name,
            password="empty",
            realms_topics=self.settings.realms_topics,
            request_prefill=self.settings.request_prefill,
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            logger.debug(subscription.model_dump())
            async with session.post(
                f"{self.settings.provisioning_api_url}/admin/v1/subscriptions",
                json=subscription.model_dump(),
                auth=aiohttp.BasicAuth(
                    admin_settings.admin_username, admin_settings.admin_password
                ),
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(
                f"{self.settings.consumer_registration_url}/subscriptions/{self.settings.consumer_name}",
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self) -> Subscription:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.settings.consumer_registration_url}/subscriptions/{self.settings.consumer_name}"
            ) as response:
                data = await response.json()
                return Subscription.model_validate(data)

    async def get_subscription_messages(
        self,
        count: Optional[int] = None,
        timeout: Optional[float] = None,
        pop: Optional[bool] = None,
        force: Optional[bool] = None,
    ) -> List[ProvisioningMessage]:
        _params = {
            "count": count,
            "timeout": timeout,
            "pop": pop,
            "force": force,
        }
        params = {k: v for k, v in _params.items() if v is not None}

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.settings.consumer_messages_url}/subscriptions/{self.settings.consumer_name}/messages",
                params=params,
            ) as response:
                msgs = await response.json()
                return [ProvisioningMessage.model_validate(msg) for msg in msgs]

    async def set_message_status(self, reports: List[MessageProcessingStatusReport]):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.settings.consumer_messages_url}/subscriptions/{self.settings.consumer_name}/messages-status/",
                json=[report.model_dump() for report in reports],
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[Subscription]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{self.settings.consumer_registration_url}/subscriptions"
            ) as response:
                data = await response.json()
                # TODO: parse a list of subscriptions instead
                return [Subscription.model_validate(data)]

    # FIXME: What is the purpose of this method? It looks like it wants to publish_event via Event API
    async def submit_message(
        self, realm: str, topic: str, body: Dict[str, Any], name: str
    ):
        message = Event(realm=realm, topic=topic, body=body)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{self.settings.consumer_registration_url}/messages",
                json=message.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass


class MessageHandler:
    def __init__(
        self,
        client: AsyncClient,
        callbacks: List[Callable[[Message], Coroutine[None, None, None]]],
        pop_after_handling: bool = True,
        message_limit: Optional[int] = None,
    ):
        """
        Each callback should be an asynchronous function to facilitate downstream asynchronous operations.
        To prevent race conditions between message processing and callback execution,
        each message and its callbacks are handled sequentially.

        Args:
            client: AsyncClient
            subscription_name: The name of the target subscription to listen on.
            callbacks: A list of asynchronous callback functions, each accepting a single message object as a parameter.
            message_limit: An optional integer specifying the maximum number of messages to process,
                primarily to facilitate testing.
            pop_after_handling: If False, messages are acknowledged immediately upon reception
                rather than after all callbacks for the message have been successfully executed.
        """
        if not callbacks:
            raise ValueError("Callback functions can't be empty")
        self.client = client
        self.callbacks = callbacks
        self.pop_after_handling = pop_after_handling
        self.message_limit = message_limit

    async def _callback_wrapper(
        self,
        message: ProvisioningMessage,
        callback: Callable[[Message], Coroutine[None, None, None]],
    ):
        """
        Wrapper around a client's callback function to encapsulate
        error handling and message acknowledgement
        """
        # TODO: Message is not enough, we need a specific ClientMessage, that includes for example num_redelivered
        msg = Message(
            publisher_name=message.publisher_name,
            ts=message.ts,
            realm=message.realm,
            topic=message.topic,
            body=message.body,
        )
        await callback(msg)
        if not self.pop_after_handling:
            return
        try:
            # TODO: Retry acknowledgement
            report = MessageProcessingStatusReport(
                status=MessageProcessingStatus.ok,
                message_seq_num=message.sequence_number,
                publisher_name=message.publisher_name,
            )
            await self.client.set_message_status([report])
        except (
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            aiohttp.ClientResponseError,
        ) as exc:
            # TODO: Test this
            logger.error(
                "Failed to acknowledge message. It will be redelivered later...",
                exc.message,
            )

    async def run(
        self,
    ):
        """
        This method is designed for asynchronous execution, either by awaiting it within an async context
        or using `asyncio.run()`.
        It continuously listens for messages, either indefinitely or until a specified message limit is reached, and
        invokes a series of callbacks for each message.
        """
        counter = 0

        while True:
            messages = await self.client.get_subscription_messages(
                count=1,
                timeout=10,
                # TODO: pop is broken serverside at the moment
                # pop= not pop_after_handling,
            )

            for message in messages:
                for callback in self.callbacks:
                    await self._callback_wrapper(message, callback)
                if self.message_limit:
                    counter += 1
                    if counter >= self.message_limit:
                        return
