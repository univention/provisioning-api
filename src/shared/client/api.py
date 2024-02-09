# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import Any, Callable, Coroutine, Dict, List, Optional

import aiohttp

from shared.models import (
    Subscription,
    NewSubscription,
    MessageProcessingStatus,
    MessageProcessingStatusReport,
    Event,
)

import shared.models.api
from shared.models.queue import MQMessage

import shared.models.api
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
            # TODO: do this with propper logging
            print(subscription.model_dump())
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

    async def on_message(
        self,
        name: str,
        callbacks: List[Callable[[Message], Coroutine[None, None, None]]] = [],
        message_limit: Optional[int] = None,
        pop_after_handling: bool = True,
    ):
        """
        This method is designed for asynchronous execution, either by awaiting it within an async context
        or using `asyncio.run()`.
        It continuously listens for messages, either indefinitely or until a specified message limit is reached, and
        invokes a series of callbacks for each message. Each callback should be an asynchronous function
        to facilitate downstream asynchronous operations. To prevent race conditions between message processing and
        callback execution, each message and its callbacks are handled sequentially.

        Args:
            name: The name of the target subscription to listen on.
            callbacks: A list of asynchronous callback functions, each accepting a single message object as a parameter.
            message_limit: An optional integer specifying the maximum number of messages to process,
                primarily to facilitate testing.
            pop_after_handling: If False, messages are acknowledged immediately upon reception
                rather than after all callbacks for the message have been successfully executed.
        """

        if not callbacks:
            return
        counter = 0

        while True:
            messages = await self.get_subscription_messages(
                name,
                count=1,
                timeout=10,
                # TODO: pop is broken serverside at the moment
                # pop=True,
            )
            if not messages:
                continue
                # TODO: Remove after debugging stage
            elif len(messages) > 1:
                raise ValueError("Somehow recieved multiple messages")

            print("recieved message")

            for callback in callbacks:
                try:
                    print("executing callback")
                    await callback(Message.model_validate(messages[0].data))
                    if pop_after_handling:
                        await self.set_message_status(
                            name,
                            messages[0],
                            shared.models.api.MessageProcessingStatus.ok,
                        )
                except Exception as exc:
                    # TODO: better error handling
                    breakpoint()
                    print(exc)

            if message_limit:
                counter += 1
                if counter >= message_limit:
                    return
