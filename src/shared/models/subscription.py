# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import enum
from typing import List

from pydantic import Field, BaseModel


class FillQueueStatus(str, enum.Enum):
    # Pre-filling the queue was not yet started.
    pending = "pending"
    # The queue is being pre-filled.
    running = "running"
    # The pre-fill task failed.
    failed = "failed"
    # The queue was pre-filled successfully.
    done = "done"


class Subscription(BaseModel):
    """A registered subscriber."""

    name: str = Field(description="The identifier of the subscription.")

    realms_topics: List[str] = Field(
        description="A list of `realm:topic` that this subscription subscribes to, e.g. `udm:users/user`."
    )

    request_prefill: bool = Field(
        description="Whether pre-filling of the queue was requested."
    )

    prefill_queue_status: FillQueueStatus = Field(
        description="Pre-filling the queue: status."
    )
