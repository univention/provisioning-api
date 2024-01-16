# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Annotated

from fastapi import Depends

from shared.adapters.nats_adapter import NatsMQAdapter
from shared.models import Message


class EventsPort:
    def __init__(self):
        self.message_queue = NatsMQAdapter()

    @staticmethod
    async def port_dependency():
        port = EventsPort()
        await port.message_queue.connect()
        try:
            yield port
        finally:
            await port.close()

    async def close(self):
        await self.message_queue.close()

    async def add_live_event(self, event: Message):
        # TODO: define the name "incoming" globally or handle it differently alltogether

        await self.message_queue.add_message("incoming", event)


EventsPortDependency = Annotated[EventsPort, Depends(EventsPort.port_dependency)]
