from typing import List, Tuple

from pydantic import BaseModel


class Publisher(BaseModel):
    """The base class for a registered publisher."""

    # The identifier of the publisher.
    name: str

    # A list of `(realm, topic)` that this publisher may provide.
    realms_topics: List[Tuple[str, str]]