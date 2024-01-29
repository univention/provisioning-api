# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Tuple

from pydantic import BaseModel, Field


class Publisher(BaseModel):
    """The base class for a registered publisher."""

    name: str = Field(description="The identifier of the publisher.")

    realms_topics: List[Tuple[str, str]] = Field(
        description=" A list of `(realm, topic)` that this publisher may provide."
    )
