# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Optional

from univention.provisioning.adapters.nats_adapter import NatsMQAdapter, messagepack_encoder

from univention.provisioning.backends import message_queue
from univention.provisioning.models.message import Message

from .config import LdapProducerSettings, ldap_producer_settings


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
        await self.mq_adapter.close()

    async def add_message(self, stream: str, subject: str, message: Message):
        await self.mq_adapter.add_message(stream, subject, message, binary_encoder=messagepack_encoder)

    async def ensure_stream(self, stream: str, manual_delete: bool, subjects: Optional[List[str]] = None):
        await self.mq_adapter.ensure_stream(stream, manual_delete, subjects)
