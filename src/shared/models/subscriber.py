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


class Subscriber(BaseModel):
    """A registered subscriber."""

    name: str = Field(description="The identifier of the subscriber.")

    realms_topics: List[str] = Field(
        description="A list of `(realm, topic)` that this subscriber subscribes to."
    )

    fill_queue: bool = Field(
        description="Whether pre-filling of the queue was requested."
    )

    fill_queue_status: FillQueueStatus = Field(
        description="Pre-filling the queue: status."
    )
