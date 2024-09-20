# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import enum
from typing import List

from pydantic import BaseModel, Field

REALM_TOPIC_PREFIX = "realm:topic"


class FillQueueStatus(str, enum.Enum):
    # Pre-filling the queue was not yet started.
    pending = "pending"
    # The queue is being pre-filled.
    running = "running"
    # The pre-fill task failed.
    failed = "failed"
    # The queue was pre-filled successfully.
    done = "done"


class FillQueueStatusReport(BaseModel):
    """Update a subscription's prefill queue status."""

    status: FillQueueStatus = Field(description="State of the prefill process.")


class Subscription(BaseModel):
    """A registered subscription."""

    name: str = Field(description="The identifier of the subscription.")

    realms_topics: List[str] = Field(
        description="A list of `realm:topic` that this subscription subscribes to, e.g. `udm:users/user`."
    )

    request_prefill: bool = Field(description="Whether pre-filling of the queue was requested.")

    prefill_queue_status: FillQueueStatus = Field(description="Pre-filling the queue: status.")


class Bucket(str, enum.Enum):
    subscriptions = "SUBSCRIPTIONS"
    credentials = "CREDENTIALS"
    cache = "CACHE"
