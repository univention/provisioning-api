# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import json

from datetime import datetime
import logging

import shared.models

from prefill.base import PreFillService
from prefill.port import PrefillPort
from consumer.subscriptions.service.subscription import match_subscription
from shared.models import FillQueueStatus
from shared.models.queue import PrefillMessage

logger = logging.getLogger(__name__)


class UDMPreFill(PreFillService):
    def __init__(self, port: PrefillPort):
        super().__init__()
        self._port = port
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    async def handle_requests_to_prefill(self):
        self._logger.info("Handling the requests to prefill")
        await self._port.subscribe_to_queue("prefill")
        while True:
            self._logger.info("Waiting for the request...")
            msg = await self._port.wait_for_event()
            await msg.in_progress()

            try:
                data = json.loads(msg.data)
                validated_msg = PrefillMessage.model_validate(data)

                self._subscriber_name = validated_msg.subscriber_name
                self._topic = validated_msg.topic
                self._realm = validated_msg.realm

                await self._port.update_subscriber_queue_status(
                    self._subscriber_name, FillQueueStatus.running
                )

                if self._realm == "udm":
                    await self.fetch()
                else:
                    # FIXME: unhandled realm
                    logging.error("Unhandled realm: %s", self._realm)

            except Exception as exc:
                logger.error("Failed to launch pre-fill handler: %s", exc)

                await msg.nak()  # TODO: handle failed requests

                await self._port.update_subscriber_queue_status(
                    self._subscriber_name, FillQueueStatus.failed
                )

            else:
                await msg.ack()
                await self._port.update_subscriber_queue_status(
                    self._subscriber_name, FillQueueStatus.done
                )

    async def fetch(self):
        """
        Start fetching all data for the given topic.
        Find all UDM object types which match the given topic.
        """

        udm_modules = await self._port.get_object_types()
        udm_match = [
            module
            for module in udm_modules
            if match_subscription("udm", self._topic, "udm", module["name"])
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

        message = shared.models.Message(
            publisher_name="udm-pre-fill",
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={
                "old": None,
                "new": obj,
            },
        )
        self._logger.info("Sending to the consumer prefill queue from: %s", url)

        await self._port.send_prefill_message(self._subscriber_name, message)
