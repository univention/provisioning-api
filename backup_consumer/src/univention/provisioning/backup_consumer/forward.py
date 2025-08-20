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
    subject: str = "stream:incoming",
) -> None:
    nc = NATS()
    await nc.connect(servers=[server], user=user, password=password)
    try:
        js = nc.jetstream()
        await js.publish(subject, json.dumps(msg.model_dump()))
    finally:
        await nc.drain()