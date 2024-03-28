# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

from src.server.core.dispatcher.port import DispatcherPort
from src.server.core.dispatcher.service.dispatcher import DispatcherService
from daemoniker import Daemonizer


async def run_dispatcher():
    async with DispatcherPort.port_context() as port:
        service = DispatcherService(port)
        await service.dispatch_events()


def main():
    with Daemonizer():
        asyncio.run(run_dispatcher())


if __name__ == "__main__":
    main()
