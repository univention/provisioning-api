# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import Any, Optional

import aiohttp
import ssl

from .config import PrefillSettings, prefill_settings
from .retry_helper import retry
from .udm_port import UDMPort

logger = logging.getLogger(__name__)


class UDMAdapter(UDMPort):
    """
    Client for the UDM REST API, providing the interfaces required by `PrefillService` and `UDMMessagingService`.

    It is intended to be used as an async context manager:
    ```
    async with UDMAdapter(settings) as adapter:
        await adapter.get_object_types()
    ```
    """

    def __init__(self, settings: Optional[PrefillSettings] = None):
        super().__init__(settings or prefill_settings())
        self.base_url = self.settings.udm_url
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        self.udm_protocol = settings.udm_protocol
        self.auth = aiohttp.BasicAuth(self.settings.udm_username, self.settings.udm_password)
        self.headers = [("accept", "application/json")]
        self._session = None

    async def __aenter__(self) -> UDMPort:
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.close()
        return False

    async def connect(self) -> None:
        if not self._session:
            ssl_context = None
            if self.udm_protocol.startswith("https"):
                ssl_context = ssl.create_default_context()
                cacert = "/etc/ssl/certs/ca-certificates.crt"
                ssl_context.load_verify_locations(cafile=cacert)

            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self._session = aiohttp.ClientSession(auth=self.auth, connector=connector, headers=self.headers, raise_for_status=True)

    async def close(self) -> None:
        if self._session:
            await self._session.close()

    @retry(logger=logger)
    async def get_object_types(self) -> list[dict[str, Any]]:
        """Return a list of available object types.

        Each entry has the keys `name`, `title` and `href`.
        """
        async with self._session.get(f"{self.base_url}") as request:
            response = await request.json()
            return response["_links"]["udm:object-types"]

    @retry(logger=logger)
    async def list_objects(self, object_type: str, position: Optional[str] = None) -> list[str]:
        """Return the URLs of all objects for the given type."""

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

        async with self._session.get(f"{self.base_url}{object_type}/", params=params) as request:
            response = await request.json()
            n_results = response["results"]
            logger.info("Found %r results for %r.", n_results, object_type)
            if n_results > 0:
                uris = [obj["uri"] for obj in response["_embedded"]["udm:object"]]
                return uris
            else:
                return []

    @retry(logger=logger)
    async def get_object(self, url: str) -> dict[str, Any]:
        """Fetch the given UDM object."""
        async with self._session.get(url) as request:
            udm_obj = await request.json()
            udm_obj.pop("_links")
            return udm_obj
