# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
import logging

import shared.models

from prefill.base import PreFillService
from prefill.port import PrefillPort
from consumer.subscriptions.service.subscription import match_subscription


logger = logging.getLogger(__name__)


class UDMPreFill(PreFillService):
    def __init__(self, port: PrefillPort, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(f"{logger.name} <{self._subscriber_name}>")
        self._port = port

    async def fetch(self):
        """Start fetching all data for the given topic."""

        self._port = PrefillPort()._udm_adapter
        await self._port.connect()

        await self._expand_topics()

    async def _expand_topics(self):
        """Find all UDM object types which match the given topic."""

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
        """Find the DNs of all UDM objects for a object_type."""

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
        self._logger.info("Sending to queue from: %s", url)
        await self._service.add_prefill_message(self._subscriber_name, message)
