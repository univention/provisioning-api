# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import logging

from daemoniker import Daemonizer

from univention.provisioning.utils.log import setup_logging

from .config import udm_transformer_settings
from .controller import UDMTransformerController
from .port import UDMTransformerPort

UDM_TRANSFORMER_CONSUMER_NAME = "udm-transformer"


async def run_udm_transformer() -> None:
    async with UDMTransformerPort.port_context() as transformer_port:
        await UDMTransformerController(transformer_port).transform_events()


async def main():
    with Daemonizer():
        await run_udm_transformer()


if __name__ == "__main__":
    # UDM adds an unwanted handler to the root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    udm_transformer_settings = udm_transformer_settings()
    setup_logging(udm_transformer_settings.log_level)
    asyncio.run(main())
