# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

from daemoniker import Daemonizer

from univention.provisioning.utils.log import setup_logging

from .config import prefill_settings
from .port import PrefillPort
from .udm_prefill import UDMPreFill


async def run_prefill():
    async with PrefillPort.port_context() as port:
        service = UDMPreFill(port)
        await service.handle_requests_to_prefill()


def main():
    with Daemonizer():
        asyncio.run(run_prefill())


if __name__ == "__main__":
    prefill_settings = prefill_settings()
    setup_logging(prefill_settings.log_level)
    main()
