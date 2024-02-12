# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials

from shared.adapters.nats_adapter import NatsMQAdapter
from shared.config import settings
from shared.models import Message


class EventsPort:
    def __init__(self):
        self.mq_adapter = NatsMQAdapter()

    @staticmethod
    async def port_dependency():
        # FIXME: create credentials for this service
        credentials = HTTPBasicCredentials(
            username=settings.admin_username, password=settings.admin_password
        )

        port = EventsPort()
        await port.mq_adapter.connect(credentials)
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.mq_adapter.close()

    async def add_live_event(self, event: Message):
        # TODO: define the name "incoming" globally or handle it differently alltogether

        await self.mq_adapter.add_message("incoming", event)


EventsPortDependency = Annotated[EventsPort, Depends(EventsPort.port_dependency)]
