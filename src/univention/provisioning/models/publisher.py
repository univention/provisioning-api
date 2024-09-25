# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List

from pydantic import BaseModel, Field

from .subscription import RealmTopic


class Publisher(BaseModel):
    """The base class for a registered publisher."""

    name: str = Field(description="The identifier of the publisher.")

    realms_topics: List[RealmTopic] = Field(
        description="A list of realm-topic combinations that this subscriber subscribes to, "
        'e.g. [{"realm": "udm", "topic": "users/user"}].'
    )
