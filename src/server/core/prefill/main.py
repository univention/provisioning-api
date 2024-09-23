# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

from daemoniker import Daemonizer

from server.core.prefill.config import prefill_settings
from server.core.prefill.port import PrefillPort
from server.core.prefill.service.udm_prefill import UDMPreFill
from server.log import setup_logging


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
