import enum
from typing import List

import pydantic


class FillQueueStatus(str, enum.Enum):
    # Pre-filling the queue was not yet started.
    pending = "pending"
    # The queue is being pre-filled.
    running = "running"
    # The pre-fill task failed.
    failed = "failed"
    # The queue was pre-filled successfully.
    done = "done"


class Subscriber(pydantic.BaseModel):
    """A registered subscriber."""

    # The identifier of the subscriber.
    name: str

    # A list of `(realm, topic)` that this subscriber subscribes to.
    realms_topics: List[str]

    # Whether pre-filling of the queue was requested.
    fill_queue: bool

    # Pre-filling the queue: status
    fill_queue_status: FillQueueStatus
