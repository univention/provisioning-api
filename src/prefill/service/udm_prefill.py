# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import re
from datetime import datetime
import logging

from prefill.base import PreFillService
from prefill.port import PrefillPort
from shared.models import (
    FillQueueStatus,
    PrefillMessage,
    Message,
    MQMessage,
    PublisherName,
)
from shared.utils.message_ack_manager import MessageAckManager


def match_topic(sub_topic: str, module_name: str) -> bool:
    """Determines if a UDM module name matches the specified subscription topic."""

    return re.fullmatch(sub_topic, module_name) is not None


class UDMPreFill(PreFillService):
    prefill_queue = "prefill"
    prefill_failures_queue = "prefill-failures"

    def __init__(self, port: PrefillPort):
        super().__init__()
        self._port = port
        self.ack_manager = MessageAckManager()
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    async def handle_requests_to_prefill(self):
        self._logger.info("Handling the requests to prefill")
        await self._port.subscribe_to_queue(self.prefill_queue, "prefill-service")
        await self.prepare_prefill_failures_queue()

        while True:
            self._logger.info("Waiting for the request...")
            message = await self._port.wait_for_event()
            await self.ack_manager.process_message_with_ack_wait_extension(
                message, self.handle_message, self._port.acknowledge_message_in_progress
            )

    async def handle_message(self, message: MQMessage):
        self._logger.info("Received message with content: %s", message.data)
        while True:
            try:
                validated_msg = PrefillMessage.model_validate(message.data)

                if message.num_delivered > self.max_prefill_attempts:
                    await self.add_request_to_prefill_failures(validated_msg, message)
                    return

                self._subscription_name = validated_msg.subscription_name

                await self._port.create_prefill_stream(self._subscription_name)

                for realm, topic in validated_msg.realms_topics:
                    self._realm = realm
                    self._topic = topic

                    if self._realm == "udm":
                        await self.start_prefill_process()
                    else:
                        # FIXME: unhandled realm
                        self._logger.error("Unhandled realm: %s", self._realm)

            except Exception as exc:
                self._logger.error("Failed to launch pre-fill handler: %s", exc)
                await self.mark_request_as_failed()
                message.num_delivered += 1
            else:
                await self.mark_request_as_done(message)
                return

    async def start_prefill_process(self):
        self._logger.info(
            "Started the prefill for the subscriber %s with the topic %s",
            self._subscription_name,
            self._topic,
        )
        await self._port.update_subscription_queue_status(
            self._subscription_name, FillQueueStatus.running
        )
        await self.fetch()
        self._logger.info("Prefill request was processed")

    async def fetch(self):
        """
        Start fetching all data for the given topic.
        Find all UDM object types which match the given topic.
        """

        udm_modules = await self._port.get_object_types()
        udm_match = [
            module for module in udm_modules if match_topic(self._topic, module["name"])
        ]

        if len(udm_match) == 0:
            self._logger.warning("No UDM modules match object type %s", self._topic)

        for module in udm_match:
            this_topic = module["name"]
            self._logger.info("Grabbing %s objects.", this_topic)
            await self._fill_topic(this_topic)

    async def _fill_topic(self, object_type: str):
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
            await self._fill_object(url, object_type)

    async def _fill_object(self, url: str, object_type: str):
        """Retrieve the object for the given DN."""
        obj = await self._port.get_object(url)

        message = Message(
            publisher_name=PublisherName.udm_pre_fill,
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={
                "old": None,
                "new": obj,
            },
        )
        self._logger.info("Sending to the consumer prefill queue from: %s", url)

        await self._port.create_prefill_message(self._subscription_name, message)

    async def add_request_to_prefill_failures(
        self, validated_msg: PrefillMessage, message: MQMessage
    ):
        self._logger.info("Adding request to the prefill failures queue")
        await self._port.add_request_to_prefill_failures(
            self.prefill_failures_queue, validated_msg
        )
        await self._port.acknowledge_message(message)

    async def mark_request_as_done(self, msg: MQMessage):
        await self._port.acknowledge_message(msg)
        await self._port.update_subscription_queue_status(
            self._subscription_name, FillQueueStatus.done
        )

    async def mark_request_as_failed(self):
        await self._port.update_subscription_queue_status(
            self._subscription_name, FillQueueStatus.failed
        )

    async def prepare_prefill_failures_queue(self):
        await self._port.create_stream(self.prefill_failures_queue)
        await self._port.create_consumer(self.prefill_failures_queue)
