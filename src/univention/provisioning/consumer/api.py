# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import inspect
import logging
import time
from typing import Any, Callable, Coroutine, Dict, List, Optional, Tuple

import aiohttp
from jsondiff import diff

from univention.provisioning.models import (
    Event,
    Message,
    MessageProcessingStatus,
    MessageProcessingStatusReport,
    NewSubscription,
    ProvisioningMessage,
    Subscription,
)

from .config import MessageHandlerSettings, ProvisioningConsumerClientSettings

logger = logging.getLogger(__name__)


# TODO: the subscription part will be delegated to an admin using an admin API
class ProvisioningConsumerClient:
    def __init__(self, settings: Optional[ProvisioningConsumerClientSettings] = None, concurrency_limit: int = 10):
        self.settings = settings or ProvisioningConsumerClientSettings()
        auth = aiohttp.BasicAuth(
            self.settings.provisioning_api_username,
            self.settings.provisioning_api_password,
        )
        connector = aiohttp.TCPConnector(limit=concurrency_limit)
        self.session = aiohttp.ClientSession(auth=auth, connector=connector, raise_for_status=True)

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    # TODO: move this method to the AdminClient
    async def create_subscription(
        self,
        name: str,
        password: str,
        realms_topics: List[Tuple[str, str]],
        request_prefill: bool = False,
    ):
        logger.info("creating subscription for %s", str(realms_topics))
        subscription = NewSubscription(
            name=name,
            realms_topics=realms_topics,
            request_prefill=request_prefill,
            password=password,
        )

        logger.debug(subscription.model_dump())
        return await self.session.post(self.settings.subscriptions_url, json=subscription.model_dump())

    async def cancel_subscription(self, name: str):
        return await self.session.delete(f"{self.settings.subscriptions_url}/{name}")

    async def get_subscription(self, name: str) -> Subscription:
        response = await self.session.get(f"{self.settings.subscriptions_url}/{name}")
        data = await response.json()
        return Subscription.model_validate(data)

    async def get_subscription_message(
        self,
        name: str,
        timeout: Optional[float] = None,
        pop: Optional[bool] = None,
    ) -> ProvisioningMessage:
        _params = {
            "timeout": timeout,
            "pop": pop,
        }
        params = {k: v for k, v in _params.items() if v is not None}

        response = await self.session.get(f"{self.settings.subscriptions_messages_url(name)}/next", params=params)
        msg = await response.json()
        return ProvisioningMessage.model_validate(msg) if msg else msg

    async def set_message_status(self, name: str, report: MessageProcessingStatusReport):
        return await self.session.patch(
            f"{self.settings.subscriptions_messages_url(name)}/{report.message_seq_num}/status",
            json=report.model_dump(),
        )

    # TODO: move this method to the AdminClient
    async def get_subscriptions(self) -> List[Subscription]:
        response = await self.session.get(self.settings.subscriptions_url)
        data = await response.json()
        # TODO: parse a list of subscriptions instead
        return [Subscription.model_validate(data)]

    # FIXME: What is the purpose of this method? It looks like it wants to publish_event via Event API
    async def submit_message(self, realm: str, topic: str, body: Dict[str, Any], name: str):
        message = Event(realm=realm, topic=topic, body=body)

        return await self.session.post(self.settings.messages_url, json=message.model_dump())


class MessageHandler:
    def __init__(
        self,
        client: ProvisioningConsumerClient,
        callbacks: List[Callable[[Message], Coroutine[None, None, None]]],
        settings: Optional[MessageHandlerSettings] = None,
        pop_after_handling: bool = True,
        message_limit: Optional[int] = None,
    ):
        """
        Each callback should be an asynchronous function to facilitate downstream asynchronous operations.
        To prevent race conditions between message processing and callback execution,
        each message and its callbacks are handled sequentially.

        Args:
            client: ProvisioningConsumerClient
            subscription_name: The name of the target subscription to listen on.
            callbacks: A list of asynchronous callback functions, each accepting a single message object as a parameter.
            message_limit: An optional integer specifying the maximum number of messages to process,
                primarily to facilitate testing.
            pop_after_handling: If False, messages are acknowledged immediately upon reception
                rather than after all callbacks for the message have been successfully executed.
        """
        if not callbacks:
            raise ValueError("Callback functions can't be empty")
        self.settings = settings or MessageHandlerSettings()
        self.client = client
        self.subscription_name = self.client.settings.provisioning_api_username
        self.callbacks = callbacks
        self.pop_after_handling = pop_after_handling
        self.message_limit = message_limit

    async def acknowledge_message(self, message_seq_num: int) -> bool:
        logger.debug("Acknowledging message with sequence number: %r", message_seq_num)
        try:
            report = MessageProcessingStatusReport(
                status=MessageProcessingStatus.ok,
                message_seq_num=message_seq_num,
            )
            await self.client.set_message_status(self.subscription_name, report)
            return True
        except (
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            aiohttp.ClientResponseError,
        ) as exc:
            logger.error("Failed to acknowledge message. - %s", repr(exc))
            return False

    async def acknowledge_message_with_retries(self, message):
        for retries in range(self.settings.max_acknowledgement_retries + 1):
            if await self.acknowledge_message(message.sequence_number):
                logger.info("Message %r was acknowledged.", message.sequence_number)
                return

            logger.warning("Failed to acknowledge message. Retries: %d", retries)
            if retries != self.settings.max_acknowledgement_retries:
                timeout = min(2**retries / 10, 30)
                await asyncio.sleep(timeout)

        logger.error(
            "Maximum retries of %s reached. The message will be redelivered later",
            self.settings.max_acknowledgement_retries,
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
            message = await self.client.get_subscription_message(
                self.subscription_name,
                timeout=10,
                # TODO: pop is broken serverside at the moment
                # pop= not pop_after_handling,
            )
            if not message:
                continue
            logger.debug(self.debug_msg(message))
            for callback in self.callbacks:
                t0 = time.perf_counter()
                await callback(message)
                logger.debug(
                    "%r finished handling message in %.1f ms.",
                    getattr(inspect.getmodule(callback).__spec__, "name", "__main__"),
                    (time.perf_counter() - t0) * 1000,
                )
            if self.pop_after_handling:
                await self.acknowledge_message_with_retries(message)

            if self.message_limit:
                counter += 1
                if counter >= self.message_limit:
                    return

    @staticmethod
    def debug_msg(message: Message) -> str:
        msg = f"realm: {message.realm!r} topic: {message.topic!r}"
        if message.realm == "udm":
            old = message.body.old
            new = message.body.new
            if old and new:
                change = diff(message.body.old, message.body.new, syntax="rightonly")
                if old["dn"] != new["dn"]:
                    msg += " action: move"
                    msg += f" old_dn: {old['dn']}"
                    change.pop("dn", None)
                else:
                    msg += " action: update"
                msg += f" dn: {new['dn']}"
                msg += f" diff(old, new): {change!r}"
            elif not old:
                msg += " action: create"
                msg += f" dn: {new['dn']}"
            elif not new:
                msg += " action: delete"
                msg += f" dn: {old['dn']}"
            else:
                msg += " action: ERROR(No object data)"
        else:
            msg += f" body: {message.body!r}"
        return msg
