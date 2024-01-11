# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from pydantic import BaseModel, Field, field_serializer


class BaseMessage(BaseModel):
    """The common header properties of each message."""

    # The name of the publisher of the message.
    publisher_name: str
    # The timestamp when the message was received by the dispatcher.
    ts: datetime
    # The realm of the message, e.g. `udm`.
    realm: str
    # The topic of the message, e.g. `users/user`.
    topic: str

    @field_serializer("ts")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()


class Message(BaseMessage):
    """The base class for any kind of message sent via the queues."""

    # The content of the message.
    body: Dict[str, Any] = Field(
        description="The content of the message as a key/value dictionary."
    )


class UDMMessage(BaseMessage):
    """A message emitted from the UDM REST API."""

    _realm: ClassVar[str] = "udm"

    # The UDM object before the change.
    old: Dict[str, Any]
    # The UDM object after the change.
    new: Dict[str, Any]

    @classmethod
    def from_message(cls, msg: Message):
        """Try to parse a message from the queue."""
        if msg.realm != cls._realm:
            raise AttributeError

        return cls(
            publisher_name=msg.publisher_name,
            ts=msg.ts,
            realm=msg.ts,
            topic=msg.topic,
            new=msg.body.get("new", {}),
            old=msg.body.get("old", {}),
        )


class NatsMessage(BaseModel):
    subject: str = ""
    reply: str = ""
    data: dict = {}
    headers: Optional[Dict[str, str]] = None
