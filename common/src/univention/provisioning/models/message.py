# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import enum
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field, field_serializer, field_validator, model_validator
from typing_extensions import Literal, Self

from .constants import PublisherName
from .subscription import RealmTopic

LDAP_OBJECT_TYPE_FIELD = "univentionObjectType"
UDM_OBJECT_TYPE_FIELD = "objectType"


class EmptyBodyError(Exception): ...


class NoUDMTypeError(Exception): ...


class BaseMessage(BaseModel):
    """The common header properties of each message."""

    publisher_name: PublisherName = Field(description="The name of the publisher of the message.")
    ts: datetime = Field(description="The timestamp when the message was received by the dispatcher.")

    @field_serializer("ts")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()


class Body(BaseModel):
    old: Dict[str, Any] = Field(description="The LDAP/UDM object before the change.")
    new: Dict[str, Any] = Field(description="The LDAP/UDM object after the change.")

    # Temporary validator due to the hardcoded image version of udm-listener.
    # This will be removed once we switch from udm-listener to ldif-producer.
    @field_validator("old", "new", mode="before")
    @classmethod
    def set_empty_dict(cls, v: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return v or {}

    @model_validator(mode="after")
    def check_not_both_empty(self) -> Self:
        if not self.old and not self.new:
            raise EmptyBodyError("'old' and 'new' cannot be both empty.")
        return self

    @model_validator(mode="after")
    def check_has_udm_object_type(self) -> Self:
        if LDAP_OBJECT_TYPE_FIELD in self.new or LDAP_OBJECT_TYPE_FIELD in self.old:
            obj_type = LDAP_OBJECT_TYPE_FIELD
        else:
            obj_type = UDM_OBJECT_TYPE_FIELD
        if not self.new.get(obj_type) and not self.old.get(obj_type):
            raise NoUDMTypeError("No UDM type in both 'new' and 'old'.")
        return self


class LDIFProducerBody(Body):
    ldap_request_type: Literal["ADD", "MODIFY", "MODRDN", "DELETE"] = Field(description="The LDAP operation.")
    binddn: str = Field(description="The LDAP user that triggered the operation.")
    message_id: int = Field(description="An LDAP operation counter.")
    request_id: str = Field(description="Reference ID in the LDIF producer logs.")


class SimpleMessage(BaseMessage):
    """Message with a minimal payload"""

    body: Dict[str, Any] = Field(description="The content of the message as a key/value dictionary.")


class Message(BaseMessage):
    """The base class for any kind of message sent via the queues."""

    realm: str = Field(description="The realm of the message, e.g. `udm`.")
    topic: str = Field(description="The topic of the message, e.g. `users/user`.")
    body: Body = Field(description="The content of the message as a key/value dictionary.")


class LDIFProducerMessage(Message):
    """Message the LDIF Producer sends"""

    body: LDIFProducerBody = Field(description="The content of the message as a key/value dictionary.")


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
    data: Dict[str, Any]
    num_delivered: int
    sequence_number: int
    headers: Optional[Dict[str, str]] = None


class ProvisioningMessage(Message):
    sequence_number: int = Field(description="The sequence number associated with the message.")
    num_delivered: int = Field(description="The number of times that this message has been delivered.")


class PrefillMessage(BaseMessage):
    """This class represents the message used to send a request to the Prefill Service."""

    subscription_name: str = Field(description="The name of the subscription that requested the prefilling queue")
    realms_topics: List[RealmTopic] = Field(
        description="A list of realm-topic combinations that this subscriber subscribes to, "
        'e.g. [{"realm": "udm", "topic": "users/user"}].'
    )


class Event(BaseModel):
    """A message as it arrives at the API."""

    realm: str = Field(description="The realm of the message, e.g. `udm`.")
    topic: str = Field(description="The topic of the message, e.g. `users/user`.")
    body: Dict[str, Any] = Field(description="The content of the message.")


class MessageProcessingStatus(str, enum.Enum):
    # The message was processed successfully.
    ok = "ok"


class MessageProcessingStatusReport(BaseModel):
    """A subscriber reporting whether a message was processed."""

    status: MessageProcessingStatus = Field(description="Whether the message was processed by the subscriber.")
