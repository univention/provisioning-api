# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import logging
from typing import Optional
from typing import Any

import difflib

from nats.aio.client import Client as NATS
from univention.provisioning.models.message import ProvisioningMessage

logger = logging.getLogger(__name__)


async def handle_message(
    msg: Any,
    server: str,
    user: str,
    password: str,
    subject: str = "incoming",
) -> None:
    nc = NATS()
    await nc.connect(servers=[server], user=user, password=password)
    logging.info("forwarding: %s", json.dumps(msg.model_dump(), indent=2))  ## FIXME - temporary dev log message
    try:
        js = nc.jetstream()
        bytes_encoded_payload = json.dumps(msg.model_dump()).encode("utf-8")
        await js.publish(subject, bytes_encoded_payload)
    finally:
        await nc.drain()
