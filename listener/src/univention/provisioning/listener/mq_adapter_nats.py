# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# NOTE: This file is a copy of 'backends/src/univention/provisioning/backends/nats_mq.py'.
# It is required to keep this duplicate here because UCS does not yet support pydantic v2.
# This version is adapted for compatibility with pydantic v1.
# Any changes to the backend implementation should be reviewed and synchronized here as needed.

import logging
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

import msgpack
from pydantic import BaseModel, Field, root_validator
from pydantic.json import pydantic_encoder

from univention.provisioning.backends.nats_mq import LdapQueue, NatsMessageQueue

from .config import LdapProducerSettings, ldap_producer_settings
from .mq_port import MessageQueuePort

logger = logging.getLogger(__name__)

LDAP_OBJECT_TYPE_FIELD = "univentionObjectType"
UDM_OBJECT_TYPE_FIELD = "objectType"


class EmptyBodyError(Exception): ...


class NoUDMTypeError(Exception): ...


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
            raise EmptyBodyError("old' and 'new' cannot be both empty.")
        return values

    @root_validator
    def check_has_udm_object_type(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if LDAP_OBJECT_TYPE_FIELD in values.get("new") or LDAP_OBJECT_TYPE_FIELD in values.get("old"):
            obj_type = LDAP_OBJECT_TYPE_FIELD
        else:
            obj_type = UDM_OBJECT_TYPE_FIELD
        if not values.get("new").get(obj_type) and not values.get("old").get(obj_type):
            raise NoUDMTypeError("No UDM type in both 'new' and 'old'.")
        return values


# copy of Message and BaseMessage from models.message
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
    return msgpack.packb(data, default=pydantic_encoder)


class MessageQueueNatsAdapter(MessageQueuePort):
    def __init__(self, settings: Optional[LdapProducerSettings] = None):
        super().__init__(settings or ldap_producer_settings())
        self.mq: Optional[NatsMessageQueue] = None

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
        message = LdapMessage(
            publisher_name=PublisherName.ldif_producer,
            ts=datetime.now(),
            realm="ldap",
            topic="ldap",
            body=Body(new=new, old=old),
        )
        encoded_message = messagepack_encoder(message.dict())
        await self.mq.add_message(LdapQueue(), encoded_message)

    async def ensure_queue_exists(self) -> None:
        await self.mq.ensure_stream(LdapQueue())
