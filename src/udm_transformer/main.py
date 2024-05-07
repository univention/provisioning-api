# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import logging

from daemoniker import Daemonizer

from shared.models.queue import LDAP_STREAM, LDAP_SUBJECT
from udm_transformer.port import UDMMessagingPort
from udm_transformer.service.udm import UDMMessagingService

UDM_TRANSFORMER_CONSUMER_NAME = "udm-transformer"

logger = logging.getLogger(__name__)


async def run_udm_transformer():
    async with UDMMessagingPort.port_context() as transformer_port:
        udm_service = UDMMessagingService(transformer_port)

        await transformer_port.initialize_subscription(
            LDAP_STREAM, LDAP_SUBJECT, UDM_TRANSFORMER_CONSUMER_NAME
        )

        while True:
            logger.error("listening for new LDAP messages")
            message, acknowledge = await transformer_port.get_msgpack_message(
                timeout=10
            )
            if not message or not acknowledge:
                logger.error(
                    "No new LDAP messages found int the queue, continuing to wait."
                )
                continue
            try:
                await udm_service.handle_changes(
                    message.body["new"],
                    message.body["old"],
                    message.ts,
                )
            except Exception:
                logger.exception("Failed to transform message")
                raise
            await acknowledge


async def main():
    with Daemonizer():
        await run_udm_transformer()


if __name__ == "__main__":
    asyncio.run(main())
