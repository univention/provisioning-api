# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# NOTE: This file is a copy of 'backends/src/univention/provisioning/backends/nats_mq.py'.
# It is required to keep this duplicate here because UCS does not yet support pydantic v2.
# This version is adapted for compatibility with pydantic v1.
# Any changes to the backend implementation should be reviewed and synchronized here as needed.

import logging
from datetime import datetime
from typing import Any, Dict

import msgpack

from univention.provisioning.backends.nats_mq import LdapQueue, NatsMessageQueue

from .config import LdapProducerSettings
from .mq_port import MessageQueuePort

logger = logging.getLogger(__name__)


def is_udm_message(new: Dict[str, Any], old: Dict[str, Any]) -> bool:
    return bool(new.get("univentionObjectType") or old.get("univentionObjectType"))


class MessageQueueNatsAdapter(MessageQueuePort):
    def __init__(self, settings: LdapProducerSettings):
        self.settings = settings
        self.mq: NatsMessageQueue | None = None

    async def __aenter__(self):
        self.mq = NatsMessageQueue(
            self.settings.nats_server,
            self.settings.nats_user,
            self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )
        await self.mq.connect()
        return self

    async def __aexit__(self, *args):
        await self.mq.close()
        self.mq = None
        return False

    async def enqueue_change_event(self, new: Dict[str, Any], old: Dict[str, Any]) -> None:
        if not is_udm_message(new, old):
            logger.debug("Skipping non-UDM message")
            return

        message = {
            "publisher_name": "ldif-producer",
            "ts": datetime.now().isoformat(),
            "realm": "ldap",
            "topic": "ldap",
            "body": {
                "new": new,
                "old": old,
            },
        }
        encoded_message = msgpack.packb(message)
        await self.mq.add_message(LdapQueue(), encoded_message)

    async def ensure_queue_exists(self) -> None:
        await self.mq.ensure_stream(LdapQueue())
