# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import contextlib

from shared.adapters.udm_adapter import UDMAdapter


class PrefillPort:
    async def __init__(self) -> None:
        self._udm_adapter = UDMAdapter()

    @staticmethod
    @contextlib.asynccontextmanager
    async def port_context():
        port = PrefillPort()
        await port._udm_adapter.connect()

        try:
            yield port
        finally:
            await port._udm_adapter.close()

    async def get_object_types(self):
        return self._udm_adapter.get_object_types()

    async def list_objects(self, object_type):
        return self._udm_adapter.list_objects(object_type)

    async def get_object(self, url):
        return self._udm_adapter.get_object(url)
