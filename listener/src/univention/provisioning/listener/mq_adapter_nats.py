# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
from typing import Any, Dict, Optional

import msgpack

from univention.provisioning.backends import message_queue
from univention.provisioning.backends.message_queue import MessageQueue
from univention.provisioning.models.constants import LDAP_PRODUCER_QUEUE_NAME, PublisherName
from univention.provisioning.models.message import Body, Message

from .config import LdapProducerSettings, ldap_producer_settings
from .mq_port import MessageQueuePort

LDAP_SUBJECT = "ldap-producer-subject"


def messagepack_encoder(data: Any) -> bytes:
    return msgpack.packb(data)


class MessageQueueNatsAdapter(MessageQueuePort):
    def __init__(self, settings: Optional[LdapProducerSettings] = None):
        super().__init__(settings or ldap_producer_settings())
        self.mq: Optional[MessageQueue] = None

    async def __aenter__(self):
        self.mq = message_queue(
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
        message = Message(
            publisher_name=PublisherName.ldif_producer,
            ts=datetime.now(),
            realm="ldap",
            topic="ldap",
            body=Body(new=new, old=old),
        )
        await self.mq.add_message(LDAP_PRODUCER_QUEUE_NAME, LDAP_SUBJECT, message, binary_encoder=messagepack_encoder)

    async def ensure_queue_exists(self) -> None:
        await self.mq.ensure_stream(LDAP_PRODUCER_QUEUE_NAME, False, [LDAP_SUBJECT])
