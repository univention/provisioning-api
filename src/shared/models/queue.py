# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
from typing import Any, ClassVar, Dict, Optional

from pydantic import BaseModel, Field, field_serializer


class BaseMessage(BaseModel):
    """The common header properties of each message."""

    publisher_name: str = Field(description="The name of the publisher of the message.")

    ts: datetime = Field(
        description="The timestamp when the message was received by the dispatcher."
    )

    realm: str = Field(description="The realm of the message, e.g. `udm`.")

    topic: str = Field(description="The topic of the message, e.g. `users/user`.")

    @field_serializer("ts")
    def serialize_dt(self, dt: datetime, _info):
        return dt.isoformat()


class Message(BaseMessage):
    """The base class for any kind of message sent via the queues."""

    body: Dict[str, Any] = Field(
        description="The content of the message as a key/value dictionary."
    )

    receivers: str = Field(
        default="All",
        description=(
            "Specifies the target subscriber when their queue is temporarily blocked. "
            "The default is 'All' to broadcast the message to all subscribers."
        ),
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
