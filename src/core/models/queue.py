from datetime import datetime
import json
from typing import Any, ClassVar, Dict, Self

from pydantic import BaseModel


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


class Message(BaseMessage):
    """The base class for any kind of message sent via the queues."""

    # The content of the message.
    body: Dict[str, Any]

    def flatten(self) -> Dict[str, str]:
        """Convert the message into a simple dict.

        Substructures inside the `body` dict are serialized using JSON.

        This is necessary to store the message in a Redis stream.
        """

        return dict(
            publisher_name=self.publisher_name,
            ts=self.ts.isoformat(),
            realm=self.realm,
            topic=self.topic,
            body=json.dumps(self.body),
        )

    @classmethod
    def inflate(cls, data: Dict[str, str]) -> Self:
        """Convert the dictionary into its original form.

        This is the opposite of `.flatten()`.
        It expands the serialized `body` back into `dict`s.
        """

        return Message(
            publisher_name=data["publisher_name"],
            ts=datetime.fromisoformat(data["ts"]),
            realm=data["realm"],
            topic=data["topic"],
            body=json.loads(data["body"]),
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
