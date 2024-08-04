# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
import re
from datetime import datetime

from pydantic import ValidationError

from server.adapters.nats_adapter import Empty
from server.core.prefill.port import PrefillPort
from server.utils.message_ack_manager import MessageAckManager
from univention.provisioning.models import (
    PREFILL_STREAM,
    PREFILL_SUBJECT_TEMPLATE,
    FillQueueStatus,
    MQMessage,
    PrefillMessage,
)
from univention.provisioning.models.queue import Body, Message, PublisherName, SimpleMessage


class PrefillFailedError(Exception): ...


def match_topic(sub_topic: str, module_name: str) -> bool:
    """Determines if a UDM module name matches the specified subscription topic."""

    return re.fullmatch(sub_topic, module_name) is not None


class UDMPreFill:
    PREFILL_FAILURES_STREAM = "prefill-failures"

    def __init__(self, port: PrefillPort):
        super().__init__()
        self._port = port
        self.ack_manager = MessageAckManager(ack_wait=30, ack_threshold=5)
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)
        self.max_prefill_attempts = port.settings.max_prefill_attempts

    async def handle_requests_to_prefill(self):
        self._logger.info("Handling the requests to prefill")

        await self.prepare_prefill_failures_queue()
        await self._port.initialize_subscription(PREFILL_STREAM, False, None)

        while True:
            self._logger.info("Waiting for new prefill requests...")
            try:
                message, acknowledgements = await self._port.get_one_message()
            except Empty:
                continue

            message_handler = self.handle_message(message)
            try:
                await self.ack_manager.process_message_with_ack_wait_extension(
                    message_handler, acknowledgements.acknowledge_message_in_progress
                )
            except PrefillFailedError:
                self._logger.warning(
                    "A recoverable error happened while processing the prefill request. "
                    "The prefill request will be scheduled for redelivery and retried at a later time."
                )
                await acknowledgements.acknowledge_message_negatively()
                continue
            except ValidationError:
                await acknowledgements.acknowledge_message_negatively()
                raise
            except Exception:
                self._logger.exception("Unknown error occured while processing the prefill request.")
                await acknowledgements.acknowledge_message_negatively()
                raise

            await acknowledgements.acknowledge_message()

    async def handle_message(self, message: MQMessage):
        self._logger.info("Received message with content: %s", message.data)
        try:
            validated_message = PrefillMessage.model_validate(message.data)
        except ValidationError:
            self._logger.exception("failed to parse message queue message: %r", message.data)
            raise

        if self.max_prefill_attempts != -1 and message.num_delivered > self.max_prefill_attempts:
            self._logger.error(
                "The maximum number of retries for prefilling the subscription %s has been reached. "
                "The prefill will not be retried again and the subscription will be marked as failed. "
                "To trigger the prefill again, delete and recreate the subscription."
            )
            await self.add_to_failure_queue(message.data)
            await self._port.update_subscription_queue_status(
                validated_message.subscription_name, FillQueueStatus.failed
            )
            return

        await self._handle_message(validated_message)

        await self._port.update_subscription_queue_status(validated_message.subscription_name, FillQueueStatus.done)

    async def _handle_message(self, message: PrefillMessage):
        await self._port.remove_old_messages_from_prefill_subject(
            message.subscription_name,
            PREFILL_SUBJECT_TEMPLATE.format(subscription=message.subscription_name),
        )

        for realm, topic in message.realms_topics:
            if realm != "udm":
                # FIXME: unhandled realm
                self._logger.error("Unhandled realm: %s", realm)
                continue

            self._logger.info(
                "Started the prefill for the subscriber %s with the topic %s",
                message.subscription_name,
                topic,
            )
            await self._port.update_subscription_queue_status(message.subscription_name, FillQueueStatus.running)
            await self.fetch_udm(message.subscription_name, topic)

    async def fetch_udm(self, subscription_name: str, topic: str):
        """
        Start fetching all data for the given topic.
        Find all UDM object types which match the given topic.
        """

        udm_modules = await self._port.get_object_types()
        udm_match = [module for module in udm_modules if match_topic(topic, module["name"])]

        if len(udm_match) == 0:
            self._logger.warning("No UDM modules match object type %s", topic)

        for module in udm_match:
            this_topic = module["name"]
            self._logger.info("Grabbing %s objects.", this_topic)
            await self._fill_udm_topic(this_topic, subscription_name)

    async def _fill_udm_topic(self, object_type: str, subscription_name: str):
        """Find the DNs of all UDM objects for an object_type."""

        # Note: the size of the HTTP response is limited in the UDM REST API container
        # by the UCR variable `directory/manager/web/sizelimit`
        # (default: 400.000 bytes).
        #
        # We should probably use pagination to fetch the objects but the parameters
        # `page` and `limit` are marked as "Broken/Experimental" in the UDM REST API.
        #
        # For now, first request all users without their properties,
        # then do one request per user to fetch the whole object.

        urls = await self._port.list_objects(object_type)
        for url in urls:
            self._logger.info("Grabbing object from: %s", url)
            await self._fill_object(url, object_type, subscription_name)

    async def _fill_object(self, url: str, object_type: str, subscription_name: str):
        """Retrieve the object for the given DN."""
        obj = await self._port.get_object(url)

        message = Message(
            publisher_name=PublisherName.udm_pre_fill,
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body=Body(old={}, new=obj),
        )
        self._logger.info("Sending to the consumer prefill queue from: %s", url)

        await self._port.create_prefill_message(
            subscription_name,
            PREFILL_SUBJECT_TEMPLATE.format(subscription=subscription_name),
            message,
        )

    async def add_to_failure_queue(self, data: dict) -> None:
        self._logger.info("Adding request to the prefill failures queue")
        message = SimpleMessage(
            publisher_name=PublisherName.udm_pre_fill,
            ts=datetime.now(),
            body=data,
        )
        await self._port.add_request_to_prefill_failures(
            self.PREFILL_FAILURES_STREAM, self.PREFILL_FAILURES_STREAM, message
        )

    async def prepare_prefill_failures_queue(self):
        await self._port.ensure_stream(self.PREFILL_FAILURES_STREAM, False)
        await self._port.ensure_consumer(self.PREFILL_FAILURES_STREAM)
