import enum
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, Field


class NewSubscriber(BaseModel):
    """Request to register a subscriber."""

    name: str = Field(description="The identifier of the subscriber.")
    realms_topics: List[Tuple[str, str]] = Field(
        description="A list of `(realm, topic)` tuples that this subscriber subscribes to."
    )
    fill_queue: bool = Field(
        description="Whether pre-filling of the queue was requested."
    )


class NewMessage(BaseModel):
    """
    A message as it arrives on the API.
    """

    # The realm of the message, e.g. `udm`.
    realm: str
    # The topic of the message, e.g. `users/user`.
    topic: str
    # The content of the message.
    body: Dict[str, Any]


class MessageProcessingStatus(str, enum.Enum):
    # Message was processed successfully.
    ok = "ok"


class MessageProcessingStatusReport(BaseModel):
    """A subscriber reporting whether a message was processed."""

    # Whether the message was processed by the subscriber.
    status: MessageProcessingStatus
