#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import argparse
import asyncio
import logging
import sys
from importlib.metadata import version
from typing import Sequence

from aiohttp import ClientResponseError

from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
)
from univention.provisioning.models.message import ProvisioningMessage, RealmTopic

from .pretty_print import handle_any_message, handle_udm_message

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"

logger = logging.getLogger(__name__)


async def handle_message(message: ProvisioningMessage):
    if message.realm == "udm":
        handle_udm_message(message)
    else:
        handle_any_message(message)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--realm_topic",
        action="append",
        help="{REALM:TOPIC} that the example client should stream, example udm:users/user",
    )
    parser.add_argument(
        "--prefill",
        action="store_true",
        help="request prefill for the example client subscription",
    )
    parser.add_argument("--admin_username")
    parser.add_argument("--admin_password")
    arguments = parser.parse_args(argv)
    return arguments


async def _create_subscription(arguments, base_url):
    admin_settings = ProvisioningConsumerClientSettings(
        provisioning_api_username=arguments.admin_username,
        provisioning_api_password=arguments.admin_password,
        provisioning_api_base_url=base_url,
    )
    realms_topics_args = [realm_topic.split(":") for realm_topic in arguments.realm_topic]
    assert all(len(x) == 2 for x in realms_topics_args), "'realm_topic' argument must contain exactly one colon."
    prefill = arguments.prefill
    async with ProvisioningConsumerClient(admin_settings) as admin_client:
        try:
            await admin_client.create_subscription(
                admin_settings.provisioning_api_username,
                admin_settings.provisioning_api_password,
                [RealmTopic(realm=realm, topic=topic) for realm, topic in realms_topics_args],
                prefill,
            )
        except ClientResponseError as e:
            logger.warning("%s, Client already exists", e)


async def main(settings: ProvisioningConsumerClientSettings) -> None:
    arguments = parse_args(sys.argv[1:])

    if len(sys.argv) > 1:
        await _create_subscription(arguments, settings.provisioning_api_base_url)

    logger.info("Listening for messages")
    async with ProvisioningConsumerClient(settings) as client:
        await MessageHandler(client, [handle_message]).run()


def run():
    settings = ProvisioningConsumerClientSettings()
    logging.basicConfig(format=LOG_FORMAT, level=settings.log_level)
    logger.info("args: %r", sys.argv)
    logger.info("Using 'nubus-provisioning-consumer' library version %r.", version("nubus-provisioning-consumer"))
    asyncio.run(main(settings))


if __name__ == "__main__":
    run()
