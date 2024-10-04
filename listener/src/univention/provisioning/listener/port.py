# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Optional, Any
import msgpack
from univention.provisioning.adapters.message_queue import MessageQueue
from univention.provisioning.adapters.nats_mq import NatsMQAdapter

from univention.provisioning.backends import message_queue
from univention.provisioning.models.message import Message

from .config import LdapProducerSettings, ldap_producer_settings


def messagepack_encoder(data: Any) -> bytes:
    return msgpack.packb(data)


class LDAPProducerPort:
    def __init__(self, settings: Optional[LdapProducerSettings] = None):
        self.settings = settings or ldap_producer_settings()
        self.mq = message_queue(
            self.settings.nats_server,
            self.settings.nats_user,
            self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )

    async def __aenter__(self):
        await self.mq.connect()
        return self

    async def __aexit__(self, *args):
        await self.mq.close()

    async def add_message(self, stream: str, subject: str, message: Message):
        await self.mq.add_message(stream, subject, message, binary_encoder=messagepack_encoder)

    async def ensure_stream(self, stream: str, manual_delete: bool, subjects: Optional[List[str]] = None):
        await self.mq.ensure_stream(stream, manual_delete, subjects)
