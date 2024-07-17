# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Optional

from provisioning_listener.config import LdapProducerSettings
from server.adapters.nats_adapter import NatsMQAdapter, messagepack_encoder
from univention.provisioning.models.queue import Message


class LDAPProducerPort:
    def __init__(self, settings: Optional[LdapProducerSettings] = None):
        self.settings = settings or LdapProducerSettings()
        self.mq_adapter = NatsMQAdapter()

    async def __aenter__(self):
        await self.mq_adapter.connect(
            self.settings.nats_server,
            self.settings.nats_user,
            self.settings.nats_password,
            max_reconnect_attempts=self.settings.nats_max_reconnect_attempts,
        )
        return self

    async def __aexit__(self, *args):
        await self.mq_adapter.close()

    async def add_message(self, stream: str, subject: str, message: Message):
        await self.mq_adapter.add_message(stream, subject, message, binary_encoder=messagepack_encoder)

    async def ensure_stream(self, stream: str, subjects: Optional[List[str]] = None):
        await self.mq_adapter.ensure_stream(stream, subjects)
