# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import enum
from typing import Any, Dict, List, Tuple
from pydantic import BaseModel, Field
from shared.models import PublisherName


class NewSubscription(BaseModel):
    """Request to register a subscription."""

    name: str = Field(description="The identifier of the subscription.")
    realms_topics: List[Tuple[str, str]] = Field(
        description="A list of `(realm, topic)` lists that this subscriber subscribes to, e.g. [('udm', 'users/user')]."
    )
    request_prefill: bool = Field(
        description="Whether pre-filling of the queue was requested."
    )
    password: str = Field(description="Password for subscription registration.")


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
    message_seq_num: int = Field(
        description="A sequence number representing the processed message."
    )
    publisher_name: PublisherName = Field(
        description="The name of the publisher of the message."
    )
