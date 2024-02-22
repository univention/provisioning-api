# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime

from enum import Enum
from typing import Any, ClassVar, Dict, Optional, List, Tuple

from pydantic import BaseModel, Field, field_serializer


class PublisherName(str, Enum):
    udm_listener = "udm-listener"
    udm_pre_fill = "udm-pre-fill"
    consumer_registration = "consumer-registration"
    consumer_client_test = "consumer_client_test"


class BaseMessage(BaseModel):
    """The common header properties of each message."""

    publisher_name: PublisherName = Field(
        description="The name of the publisher of the message."
    )

    ts: datetime = Field(
        description="The timestamp when the message was received by the dispatcher."
    )

    @field_serializer("ts")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()


class Message(BaseMessage):
    """The base class for any kind of message sent via the queues."""

    realm: str = Field(description="The realm of the message, e.g. `udm`.")

    topic: str = Field(description="The topic of the message, e.g. `users/user`.")

    body: Dict[str, Any] = Field(
        description="The content of the message as a key/value dictionary."
    )


class PrefillMessage(BaseMessage):
    """This class represents the message used to send a request to the Prefill Service."""

    subscription_name: str = Field(
        description="The name of the subscription that requested the prefilling queue"
    )

    realms_topics: List[Tuple[str, str]] = Field(
        description="A list of `(realm, topic)` that this subscriber subscribes to, e.g. [('udm', 'users/user')]."
    )


class UDMMessage(BaseMessage):
    """A message emitted from the UDM REST API."""

    _realm: ClassVar[str] = "udm"

    old: Dict[str, Any] = Field(description="The UDM object before the change.")

    new: Dict[str, Any] = Field(description="The UDM object after the change.")

    @classmethod
    def from_message(cls, msg: Message):
        """Try to parse a message from the queue."""
        if msg.realm != cls._realm:
            raise AttributeError

        return cls(
            publisher_name=msg.publisher_name,
            ts=msg.ts,
            realm=msg.realm,
            topic=msg.topic,
            new=msg.body.get("new", {}),
            old=msg.body.get("old", {}),
        )


class MQMessage(BaseModel):
    subject: str
    reply: str
    data: dict
    num_delivered: int
    sequence_number: int
    headers: Optional[Dict[str, str]] = None


class ProvisioningMessage(Message):
    sequence_number: int = Field(
        description="The sequence number associated with the message."
    )
