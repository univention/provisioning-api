# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import msgpack
from pydantic import BaseModel, Field, root_validator

from univention.provisioning.backends import message_queue
from univention.provisioning.backends.message_queue import MessageQueue

from .config import LdapProducerSettings, ldap_producer_settings
from .mq_port import MessageQueuePort

LDAP_SUBJECT = "ldap-producer-subject"
LDAP_PRODUCER_QUEUE_NAME = "ldap-producer"


class EmptyBodyError(Exception): ...


class PublisherName(str, Enum):
    udm_listener = "udm-listener"
    ldif_producer = "ldif-producer"
    udm_pre_fill = "udm-pre-fill"
    consumer_registration = "consumer-registration"
    consumer_client_test = "consumer_client_test"


class Body(BaseModel):
    old: Dict[str, Any] = Field(description="The LDAP/UDM object before the change.")
    new: Dict[str, Any] = Field(description="The LDAP/UDM object after the change.")

    @root_validator
    def check_not_both_empty(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if not values.get("old") and not values.get("new"):
            raise EmptyBodyError("'old' and 'new' cannot be both empty.")
        return values


class LdapMessage(BaseModel):
    """Must be compatible with both pydantic v1 and v2"""

    publisher_name: PublisherName = Field(description="The name of the publisher of the message.")
    ts: datetime = Field(description="The timestamp when the message was received by the dispatcher.")

    realm: str = Field(description="The realm of the message, e.g. `udm`.")
    topic: str = Field(description="The topic of the message, e.g. `users/user`.")
    body: Body = Field(description="The content of the message as a key/value dictionary.")

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }


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
        message = LdapMessage(
            publisher_name=PublisherName.ldif_producer,
            ts=datetime.now(),
            realm="ldap",
            topic="ldap",
            body=Body(new=new, old=old),
        )
        await self.mq.add_message(LDAP_PRODUCER_QUEUE_NAME, LDAP_SUBJECT, message, binary_encoder=messagepack_encoder)

    async def ensure_queue_exists(self) -> None:
        await self.mq.ensure_stream(LDAP_PRODUCER_QUEUE_NAME, False, [LDAP_SUBJECT])
