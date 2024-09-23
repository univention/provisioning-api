# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

from daemoniker import Daemonizer

from server.core.dispatcher.config import dispatcher_settings
from server.core.dispatcher.port import DispatcherPort
from server.core.dispatcher.service.dispatcher import DispatcherService
from server.log import setup_logging


async def run_dispatcher():
    async with DispatcherPort.port_context() as port:
        service = DispatcherService(port)
        await service.dispatch_events()


def main():
    with Daemonizer():
        asyncio.run(run_dispatcher())


if __name__ == "__main__":
    dispatcher_settings = dispatcher_settings()
    setup_logging(dispatcher_settings.log_level)
    main()
