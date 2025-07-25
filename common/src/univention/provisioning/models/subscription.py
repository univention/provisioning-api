# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import enum
from typing import List

from pydantic import BaseModel, Field


class FillQueueStatus(str, enum.Enum):
    # Pre-filling the queue was not yet started.
    pending = "pending"
    # The queue is being pre-filled.
    running = "running"
    # The pre-fill task failed.
    failed = "failed"
    # The queue was pre-filled successfully.
    done = "done"


class RealmTopic(BaseModel):
    """A message's realm and topic."""

    realm: str = Field(description="The realm of the message, e.g. `udm`.")
    topic: str = Field(description="The topic of the message, e.g. `users/user`.")


class BaseSubscription(BaseModel):
    """Common subscription fields."""

    name: str = Field(description="The identifier of the subscription.")
    realms_topics: List[RealmTopic] = Field(
        description="A list of realm-topic combinations that this subscriber subscribes to, "
        'e.g. [{"realm": "udm", "topic": "users/user"}].'
    )
    request_prefill: bool = Field(description="Whether pre-filling of the queue was requested.")

    def __eq__(self, other: "BaseSubscription") -> bool:
        if self.name != other.name or self.request_prefill != other.request_prefill:
            return False
        if len(self.realms_topics) != len(other.realms_topics):
            return False
        return all(realm_topic in other.realms_topics for realm_topic in self.realms_topics)


class Subscription(BaseSubscription):
    """A registered subscription."""

    prefill_queue_status: FillQueueStatus = Field(description="Pre-filling the queue: status.")

    def __eq__(self, other: "Subscription") -> bool:
        if not super().__eq__(other):
            return False
        return self.prefill_queue_status == other.prefill_queue_status

    def __hash__(self) -> int:
        return hash(self.name)


class FillQueueStatusReport(BaseModel):
    """Update a subscription's prefill queue status."""

    status: FillQueueStatus = Field(description="State of the prefill process.")


class NewSubscription(BaseSubscription):
    """Request to register a subscription."""

    password: str = Field(description="Password for subscription registration.")

    def __eq__(self, other: "NewSubscription") -> bool:
        if not super().__eq__(other):
            return False
        return self.password == other.password
