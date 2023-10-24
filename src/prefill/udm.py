import aiohttp
from datetime import datetime
import logging
from types import TracebackType
from typing import Dict, List, Optional, Type

import core.models

from core.config import settings
from prefill.base import PreFillService
from consumer.subscriptions.service.subscription import match_subscription


logger = logging.getLogger(__name__)


class UDMClient:
    """
    Client for the UDM REST API, providing the interfaces required by `UDMPreFill`.

    It is intended to be used as an async context manager:
    ```
    async with UDMClient("http://ucs/univention/udm", "Administrator", "univention") as client:
        await client.get_object_types()
    ```
    """

    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.auth = aiohttp.BasicAuth(username, password)
        self.headers = [("accept", "application/json")]
        self._session = None

    async def __aenter__(self) -> "UDMClient":
        if not self._session:
            self._session = aiohttp.ClientSession(
                auth=self.auth, headers=self.headers, raise_for_status=True
            )

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if self._session:
            await self._session.close()

    async def get_object_types(self) -> List[Dict]:
        """Return a list of available object types.

        Each entry has the keys `name`, `title` and `href`.
        """
        async with self._session.get(f"{self.base_url}/") as request:
            response = await request.json()
            return response["_links"]["udm:object-types"]

    async def list_objects(
        self, object_type: str, position: Optional[str] = None
    ) -> List[Dict]:
        """Return the URLs of all objects of the given type."""

        params = {
            "scope": "sub",
            "hidden": "true",
            "properties": ["NonExistantDummyProperty"],
            "page": "1",
            "limit": "0",
            "dir": "ASC",
        }
        if position:
            params["position"] = position

        async with self._session.get(
            f"{self.base_url}/{object_type}/", params=params
        ) as request:
            response = await request.json()
            n_results = response["results"]
            logger.info(f"Found {n_results} results for {object_type}.")
            if n_results > 0:
                uris = [obj["uri"] for obj in response["_embedded"]["udm:object"]]
                return uris
            else:
                return []

    async def get_object(self, url: str) -> Dict:
        """Fetch the given UDM object."""
        async with self._session.get(url) as request:
            udm_obj = await request.json()
            udm_obj.pop("_links")
            return udm_obj


class UDMPreFill(PreFillService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(f"{logger.name} <{self._subscriber_name}>")

    async def fetch(self):
        """Start fetching all data for the given topic."""

        async with UDMClient(
            settings.udm_url, settings.udm_username, settings.udm_password
        ) as client:
            self._client = client
            await self._expand_topics()

    async def _expand_topics(self):
        """Find all UDM object types which match the given topic."""

        udm_modules = await self._client.get_object_types()
        udm_match = [
            module
            for module in udm_modules
            if match_subscription("udm", self._topic, "udm", module["name"])
        ]

        if len(udm_match) == 0:
            self._logger.warning(f"No UDM modules match object type {self._topic}")

        for module in udm_match:
            this_topic = module["name"]
            self._logger.info(f"Grabbing {this_topic} objects.")
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

        urls = await self._client.list_objects(object_type)
        for url in urls:
            self._logger.info(f"Grabbing object from: {url}")
            await self._fill_object(url, object_type)

    async def _fill_object(self, url: str, object_type: str):
        """Retrieve the object for the given DN."""
        obj = await self._client.get_object(url)

        message = core.models.Message(
            publisher_name="udm-pre-fill",
            ts=datetime.now(),
            realm="udm",
            topic=object_type,
            body={
                "old": None,
                "new": obj,
            },
        )
        self._logger.info(f"Sending to queue from: {url}")
        await self._service.add_prefill_message(self._subscriber_name, message)
