#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import argparse
import asyncio
import logging
import sys
from importlib.metadata import version
from typing import Sequence
import os

from aiohttp import ClientResponseError

from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
)
from univention.provisioning.models.message import ProvisioningMessage, RealmTopic

from .forward import handle_message

SERVER_ROLE_CONF = "/server_role.conf"
LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"

logger = logging.getLogger(__name__)

def parse_args(argv: Sequence[str]) -> argparse.Namespace:

    parser = argparse.ArgumentParser()

    parser.add_argument("--provisioning-api-admin-user", required=True)
    parser.add_argument("--provisioning-api-admin-user-password", required=True)
    parser.add_argument("--nats-user", required=True)
    parser.add_argument("--nats-password", required=True)
    parser.add_argument("--target-nats", required=True)
    parser.add_argument("--provisioning-url", required=True)
    parser.add_argument("--stream-name", required=True)

    arguments = parser.parse_args(argv)

    if not os.path.isfile(SERVER_ROLE_CONF):
        logger.error(f"Missing server role config file at {SERVER_ROLE_CONF}")
        sys.exit(1)

    with open("/server_role.conf") as f:
        server_role = f.read().strip()
        if server_role != "domaincontroller_backup":
            logger.info("Server is not a backup. Not continuing.")
            sys.exit(0)

    return arguments


async def _create_subscription(arguments):
    admin_settings = ProvisioningConsumerClientSettings(
        provisioning_api_username=arguments.provisioning_api_admin_user,
        provisioning_api_password=arguments.provisioning_api_admin_user_password,
        provisioning_api_base_url=arguments.provisioning_url,
    )
    prefill = False
    async with ProvisioningConsumerClient(admin_settings) as admin_client:
        try:
            await admin_client.create_subscription(
                arguments.stream_name,
                admin_settings.provisioning_api_password,
                [RealmTopic(realm="udm", topic="*")], # TODO maybe not hardcode udm here?
                prefill,
            )
        except ClientResponseError as e:
            logger.warning("%s, Client already exists", e)


async def main(settings: ProvisioningConsumerClientSettings) -> None:
    arguments = parse_args(sys.argv[1:])

    if len(sys.argv) > 1:
        await _create_subscription(arguments)

    logger.info("Listening for messages")
    async with ProvisioningConsumerClient(settings) as client:

        async def wrapper_handle_message(message: ProvisioningMessage):
            await handle_message(message, arguments.target_nats, arguments.nats_user, arguments.nats_password)

        await MessageHandler(client, [wrapper_handle_message]).run()


def run():

    arguments = parse_args(sys.argv[1:])
    settings = ProvisioningConsumerClientSettings(
        provisioning_api_username=arguments.stream_name,
        provisioning_api_password=arguments.provisioning_api_admin_user_password,
        provisioning_api_base_url=arguments.provisioning_url,
    )
    logging.basicConfig(format=LOG_FORMAT, level=settings.log_level)
    logger.info("args: %r", sys.argv)
    logger.info("Using 'nubus-provisioning-consumer' library version %r.", version("nubus-provisioning-consumer"))
    asyncio.run(main(settings))


if __name__ == "__main__":
    run()
