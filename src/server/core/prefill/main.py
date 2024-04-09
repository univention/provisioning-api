# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
from server.core.prefill.port import PrefillPort
from server.core.prefill.service.udm_prefill import UDMPreFill
from daemoniker import Daemonizer


async def run_prefill():
    async with PrefillPort.port_context() as port:
        service = UDMPreFill(port)
        await service.handle_requests_to_prefill()


def main():
    with Daemonizer():
        asyncio.run(run_prefill())


if __name__ == "__main__":
    main()
