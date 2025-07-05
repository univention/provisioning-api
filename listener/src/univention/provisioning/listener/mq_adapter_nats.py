# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from typing import Any

from typing_extensions import Self

from univention.provisioning.backends_core.constants import LDAP_PRODUCER_QUEUE_NAME, PublisherName
from univention.provisioning.backends_core.ldap_message import LdapBody, LdapMessage
from univention.provisioning.backends_core.message_queue import MessageQueuePort
from univention.provisioning.backends_core.nats_mq import NatsMessageQueue
from univention.provisioning.listener.config import LdapProducerSettings
from univention.provisioning.listener.mq_port import ListenerMessageQueuePort

logger = logging.getLogger(__name__)


LDAP_SUBJECT = "ldap-producer-subject"


class MessageQueueNatsAdapter:
    def __init__(self, message_queue: MessageQueuePort):
        self.mq = message_queue

    async def __aenter__(self) -> Self:
        await self.mq.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> bool:
        await self.mq.close()
        return False

    async def enqueue_change_event(self, new: dict[str, Any], old: dict[str, Any]) -> None:
        message = LdapMessage(
            publisher_name=PublisherName.ldif_producer,
            ts=datetime.now(),
            realm="ldap",
            topic="ldap",
            body=LdapBody(new=new, old=old),
        )

        await self.mq.add_message(LDAP_PRODUCER_QUEUE_NAME, LDAP_SUBJECT, message.binary_dump())

    async def ensure_queue_exists(self) -> None:
        await self.mq.ensure_stream(LDAP_PRODUCER_QUEUE_NAME, False, [LDAP_SUBJECT])


def message_queue_nats_adapter(settings: LdapProducerSettings) -> ListenerMessageQueuePort:
    mq = NatsMessageQueue(settings)
    adapter = MessageQueueNatsAdapter(mq)
    return adapter
