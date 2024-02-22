# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

import aiohttp

from shared.models import (
    Subscription,
    NewSubscription,
    MessageProcessingStatus,
    MessageProcessingStatusReport,
    Event,
)

from shared.models.queue import MQMessage, Message

from shared.client.config import settings

logger = logging.getLogger(__file__)


# TODO: the subscription part will be delegated to an admin using an admin API
class AsyncClient:
    async def create_subscription(
        self,
        name: str,
        realms_topics: List[Tuple[str, str]],
        request_prefill: bool = False,
    ):
        logger.info("creating subscription for %s", str(realms_topics))
        subscription = NewSubscription(
            name=name, realms_topics=realms_topics, request_prefill=request_prefill
        )

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            logger.debug(subscription.model_dump())
            async with session.post(
                f"{settings.consumer_registration_url}/subscriptions",
                json=subscription.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass

    async def cancel_subscription(self, name: str):
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.delete(
                f"{settings.consumer_registration_url}/subscriptions/{name}",
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscription(self, name: str) -> Subscription:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_registration_url}/subscriptions/{name}"
            ) as response:
                data = await response.json()
                return Subscription.model_validate(data)

    async def get_subscription_messages(
        self,
        name: str,
        count: Optional[int] = None,
        timeout: Optional[float] = None,
        pop: Optional[bool] = None,
        force: Optional[bool] = None,
    ) -> List[MQMessage]:
        # TODO:return ClientMessage instead of MQMessage
        # after we have simplified the `set_message_status` request body
        _params = {
            "count": count,
            "timeout": timeout,
            "pop": pop,
            "force": force,
        }
        params = {k: v for k, v in _params.items() if v is not None}

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_messages_url}/subscriptions/{name}/messages",
                params=params,
            ) as response:
                msgs = await response.json()
                return [MQMessage.model_validate(msg) for msg in msgs]

    async def set_message_status(
        self,
        name: str,
        message: MQMessage,
        status: MessageProcessingStatus,
    ):
        report = MessageProcessingStatusReport(status=status)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.post(
                f"{settings.consumer_messages_url}/subscriptions/{name}/messages-status/",
                json={"msg": message.model_dump(), "report": report.model_dump()},
            ):
                # either return nothing or let `.post` throw
                pass

    async def get_subscriptions(self) -> List[Subscription]:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(
                f"{settings.consumer_registration_url}/subscriptions"
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
                f"{settings.consumer_registration_url}/messages",
                json=message.model_dump(),
            ):
                # either return nothing or let `.post` throw
                pass


class MessageHandler:
    def __init__(
        self,
        client: AsyncClient,
        subscription_name: str,
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
        self.subscription_name = subscription_name
        self.callbacks = callbacks
        self.pop_after_handling = pop_after_handling
        self.message_limit = message_limit

    async def _callback_wrapper(
        self,
        message: MQMessage,
        callback: Callable[[Message], Coroutine[None, None, None]],
    ):
        """
        Wrapper around a client's callback function to encapsulate
        error handling and message acknowledgement
        """
        # TODO: Message is not enough, we need a specific ClientMessage, that includes for example num_redelivered
        await callback(Message.model_validate(message.data))
        if not self.pop_after_handling:
            return
        try:
            # TODO: Retry acknowledgement
            await self.client.set_message_status(
                self.subscription_name,
                message,
                MessageProcessingStatus.ok,
            )
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
                self.subscription_name,
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
