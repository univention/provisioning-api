import enum
from typing import Any, Dict, List, Tuple

import pydantic


class NewSubscriber(pydantic.BaseModel):
    """Request to register a subscriber."""

    # The identifier of the subscriber.
    name: str

    # A list of `(realm, topic)` that this subscriber subscribes to.
    realms_topics: List[Tuple[str, str]]

    # Whether pre-filling of the queue was requested.
    fill_queue: bool


class NewMessage(pydantic.BaseModel):
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


class MessageProcessingStatusReport(pydantic.BaseModel):
    """A subscriber reporting whether a message was processed."""

    # Whether the message was processed by the subscriber.
    status: MessageProcessingStatus
