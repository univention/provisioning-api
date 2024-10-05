# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import enum
from typing import Any, Dict

from pydantic import BaseModel, Field

from univention.provisioning.models.subscription import BaseSubscription


class NewSubscription(BaseSubscription):
    """Request to register a subscription."""

    password: str = Field(description="Password for subscription registration.")

    def __eq__(self, other: "NewSubscription") -> bool:
        if not super().__eq__(other):
            return False
        return self.password == other.password


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
