#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import argparse
import asyncio
import difflib
import json
import logging
import sys
from importlib.metadata import version
from typing import Optional, Sequence

from aiohttp import ClientResponseError

from univention.provisioning.consumer import (
    MessageHandler,
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
)
from univention.provisioning.models import ProvisioningMessage

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"

logger = logging.getLogger(__name__)


def _cprint(text: str, fg: Optional[str] = None, bg: Optional[str] = None, **kwargs):
    colors = ["k", "r", "g", "y", "b", "v", "c", "w"]

    def fg_color(color):
        return str(30 + colors.index(color))

    def bg_color(color):
        return str(40 + colors.index(color))

    if fg:
        color = f"0;{fg_color(fg)}"
        if bg:
            color += f";{bg_color(bg)}"
        logger.info("\x1b[6" + color + "m" + text + "\x1b[0m", **kwargs)
    else:
        logger.info(text, **kwargs)


def print_header(msg: ProvisioningMessage, action=None):
    logger.info("")

    text = ""
    if action:
        text = f"Action: {action}  "
    else:
        text = f"Realm: {msg.realm}  "
    _cprint(
        text + f"##  Topic: {msg.topic}  " f"##  From: {msg.publisher_name}  " f"##  Time: {msg.ts}",
        fg="k",
        bg="w",
    )


def print_object(obj: dict, prefix="", **kwargs):
    lines = json.dumps(obj, indent=2).splitlines()
    for line in lines:
        _cprint(f"{prefix}{line}", **kwargs)


def print_udm_diff(old: dict, new: dict):
    olds = json.dumps(old, indent=2, sort_keys=True).splitlines()
    news = json.dumps(new, indent=2, sort_keys=True).splitlines()
    diff = difflib.unified_diff(olds, news, n=99999)
    # import sys
    # sys.stdout.writelines(diff)
    for line_number, line in enumerate(diff):
        if line_number < 3:
            continue

        if line.startswith("+"):
            _cprint(line, fg="g")
        elif line.startswith("-"):
            _cprint(line, fg="r")
        else:
            _cprint(line)


def handle_udm_message(msg: ProvisioningMessage):
    old_full = msg.body.old
    new_full = msg.body.new

    def shrink(obj, keys):
        return {key: obj.get(key) for key in keys} if obj else {}

    keep_keys = ["dn", "properties", "options", "policies"]
    old = shrink(old_full, keep_keys)
    new = shrink(new_full, keep_keys)

    if old and new:
        print_header(msg, "Object changed")
        print_udm_diff(old, new)
    elif not old:
        print_header(msg, "Object created")
        print_object(new, prefix="+ ", fg="g")
    elif not new:
        print_header(msg, "Object deleted")
        print_object(old, prefix="- ", fg="r")
    else:
        print_header(msg)
        _cprint("No object data received!", fg="r")


def handle_any_message(msg: ProvisioningMessage):
    print_header(msg)
    logger.debug(msg.body.model_dump_json(indent=2))


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


async def main(settings: ProvisioningConsumerClientSettings) -> None:
    arguments = parse_args(sys.argv[1:])

    if len(sys.argv) > 1:
        admin_settings = ProvisioningConsumerClientSettings(
            provisioning_api_username=arguments.admin_username,
            provisioning_api_password=arguments.admin_password,
            provisioning_api_base_url=settings.provisioning_api_base_url,
        )
        realms_topics = [tuple(realm_topic.split(":")) for realm_topic in arguments.realm_topic]
        prefill = arguments.prefill
        async with ProvisioningConsumerClient(admin_settings) as admin_client:
            try:
                await admin_client.create_subscription(
                    settings.provisioning_api_username,
                    settings.provisioning_api_password,
                    realms_topics,
                    prefill,
                )
            except ClientResponseError as e:
                logger.warning("%s, Client already exists", e)

    logger.info("Listening for messages")
    async with ProvisioningConsumerClient(settings) as client:
        await MessageHandler(client, [handle_message]).run()


if __name__ == "__main__":
    _settings = ProvisioningConsumerClientSettings()
    logging.basicConfig(format=LOG_FORMAT, level=_settings.log_level)
    logger.info("args: %r", sys.argv)
    logger.info("Using 'nubus-provisioning-consumer' library version %r.", version("nubus-provisioning-consumer"))
    asyncio.run(main(_settings))
