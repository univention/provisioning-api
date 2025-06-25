# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import enum
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Optional

from .basemodel_wrapper import BaseModelWrapper

try:
    from pydantic.v1 import Field, root_validator, validator
except ImportError:
    from pydantic import Field, root_validator, validator

from typing_extensions import Literal

from .constants import PublisherName
from .subscription import RealmTopic

LDAP_OBJECT_TYPE_FIELD = "univentionObjectType"
UDM_OBJECT_TYPE_FIELD = "objectType"


class EmptyBodyError(Exception): ...


class NoUDMTypeError(Exception): ...


class BaseMessage(BaseModelWrapper):
    """The common header properties of each message."""

    publisher_name: PublisherName = Field(description="The name of the publisher of the message.")
    ts: datetime = Field(description="The timestamp when the message was received by the dispatcher.")

    # No need for field_serializer in v1, use property if you need custom JSON output
    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)
        data["ts"] = self.ts.isoformat()  # override ts serialization
        return data


class Body(BaseModelWrapper):
    old: Dict[str, Any] = Field(description="The LDAP/UDM object before the change.")
    new: Dict[str, Any] = Field(description="The LDAP/UDM object after the change.")

    # Temporary validator due to the hardcoded image version of udm-listener.
    # This will be removed once we switch from udm-listener to ldif-producer.
    @validator("old", "new", pre=True)
    def set_empty_dict(cls, v):
        return v or {}

    @root_validator
    def check_not_both_empty_and_has_udm_type(cls, values):
        old = values.get("old", {})
        new = values.get("new", {})

        if not old and not new:
            raise EmptyBodyError("'old' and 'new' cannot be both empty.")

        if LDAP_OBJECT_TYPE_FIELD in new or LDAP_OBJECT_TYPE_FIELD in old:
            obj_type = LDAP_OBJECT_TYPE_FIELD
        else:
            obj_type = UDM_OBJECT_TYPE_FIELD

        if not new.get(obj_type) and not old.get(obj_type):
            raise NoUDMTypeError("No UDM type in both 'new' and 'old'.")

        return values


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


class MQMessage(BaseModelWrapper):
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


class Event(BaseModelWrapper):
    """A message as it arrives at the API."""

    realm: str = Field(description="The realm of the message, e.g. `udm`.")
    topic: str = Field(description="The topic of the message, e.g. `users/user`.")
    body: Dict[str, Any] = Field(description="The content of the message.")


class MessageProcessingStatus(str, enum.Enum):
    # The message was processed successfully.
    ok = "ok"


class MessageProcessingStatusReport(BaseModelWrapper):
    """A subscriber reporting whether a message was processed."""

    status: MessageProcessingStatus = Field(description="Whether the message was processed by the subscriber.")
