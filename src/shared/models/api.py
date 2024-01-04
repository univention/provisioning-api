# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import enum
from typing import Any, Dict, List
from pydantic import BaseModel, Field


class NewSubscriber(BaseModel):
    """Request to register a subscriber."""

    name: str = Field(description="The identifier of the subscriber.")
    realm_topic: List[str] = Field(
        description="Realm and topic that this subscriber subscribes to."
    )
    fill_queue: bool = Field(
        description="Whether pre-filling of the queue was requested."
    )


class Event(BaseModel):
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
