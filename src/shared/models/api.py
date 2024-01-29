# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import enum
from typing import Any, Dict
from pydantic import BaseModel, Field


class NewSubscription(BaseModel):
    """Request to register a subscription."""

    name: str = Field(description="The identifier of the subscription.")

    realm: str = Field(description="A `realm` that this subscriber subscribes to.")
    topic: str = Field(description="A `topic` that this subscriber subscribes to.")
    request_prefill: bool = Field(
        description="Whether pre-filling of the queue was requested."
    )


class Event(BaseModel):
    """
    A message as it arrives on the API.
    """

    realm: str = Field(description="The realm of the message, e.g. `udm`.")

    topic: str = Field(description="The topic of the message, e.g. `users/user`.")

    body: Dict[str, Any] = Field(description="The content of the message.")


class MessageProcessingStatus(str, enum.Enum):
    # Message was processed successfully.
    ok = "ok"


class MessageProcessingStatusReport(BaseModel):
    """A subscriber reporting whether a message was processed."""

    status: MessageProcessingStatus = Field(
        description="Whether the message was processed by the subscriber."
    )
