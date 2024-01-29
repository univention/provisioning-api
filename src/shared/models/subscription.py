# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import enum

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

    name: str = Field(description="The identifier of the subscriber.")

    realm: str = Field(description="A `realm` that this subscriber subscribes to.")
    topic: str = Field(description="A `topic` that this subscriber subscribes to.")

    request_prefill: bool = Field(
        description="Whether pre-filling of the queue was requested."
    )

    prefill_queue_status: FillQueueStatus = Field(
        description="Pre-filling the queue: status."
    )
