# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
import logging
from typing import List, Optional

import msgpack
from nats.aio.client import Client as NATS
from nats.js.errors import NotFoundError

from provisioning_listener.config import get_ldap_producer_settings
from server.adapters.nats_adapter import NatsKeys
from shared.models.queue import LDAP_STREAM, LDAP_SUBJECT, Message, PublisherName

logger = logging.getLogger(__name__)


class JetstreamAdapter:
    def __init__(self, server: str, user: str, password: str, **kwargs):
        self.server = server
        self.user = user
        self.password = password
        self.kwargs = kwargs
        self._nats = NATS()

    async def __aenter__(self):
        await self._nats.connect(
            self.server, user=self.user, password=self.password, **self.kwargs
        )
        self.js = self._nats.jetstream()

        return self

    async def __aexit__(self, *args):
        await self._nats.close()

    async def ensure_stream(self, stream: str, subjects: Optional[List[str]] = None):
        stream_name = NatsKeys.stream(stream)
        try:
            # TODO: do I need to validate that the stream includes the expected subjects?
            await self.js.stream_info(stream_name)
            logger.info("A nats stream with the name '%s' already exists", stream_name)
        except NotFoundError:
            await self.js.add_stream(name=stream_name, subjects=subjects or [stream])
            logger.info("A nats stream with the name '%s' was created", stream_name)


class NatsMQMessagePackAdapter:
    def __init__(self, jetstream_adapter: JetstreamAdapter):
        self._jetstream_adapter = jetstream_adapter

    async def add_message(self, stream: str, subject: str, message: Message):
        """Publish a messagepack encoded message to a NATS subject."""
        stream_name = NatsKeys.stream(stream)

        await self._jetstream_adapter.js.publish(
            subject,
            msgpack.packb(message.model_dump()),
            stream=stream_name,
        )
        logger.info(
            "Message was published to the stream: %s with the subject: %s",
            stream_name,
            subject,
        )


async def ensure_stream():
    settings = get_ldap_producer_settings()
    async with JetstreamAdapter(
        settings.nats_server, settings.nats_user, settings.nats_password
    ) as jetstream_adapter:
        await jetstream_adapter.ensure_stream(LDAP_STREAM, [LDAP_SUBJECT])


async def handle_changes(new, old):
    message = Message(
        publisher_name=PublisherName.udm_listener,
        ts=datetime.now(),
        realm="ldap",
        topic="ldap",
        body={"new": new, "old": old},
    )

    settings = get_ldap_producer_settings()

    async with JetstreamAdapter(
        settings.nats_server, settings.nats_user, settings.nats_password
    ) as jetstream_adapter:
        nats_adapter = NatsMQMessagePackAdapter(jetstream_adapter)

        await nats_adapter.add_message(LDAP_STREAM, LDAP_SUBJECT, message)
