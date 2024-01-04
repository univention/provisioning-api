# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Tuple

from pydantic import BaseModel


class Publisher(BaseModel):
    """The base class for a registered publisher."""

    # The identifier of the publisher.
    name: str

    # A list of `(realm, topic)` that this publisher may provide.
    realms_topics: List[Tuple[str, str]]
