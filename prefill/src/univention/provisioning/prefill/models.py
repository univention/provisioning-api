# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from typing import List

from pydantic import Field

from univention.provisioning.models.message import BaseMessage
from univention.provisioning.models.subscription import RealmTopic


class PrefillMessage(BaseMessage):
    """This class represents the message used to send a request to the Prefill Service."""

    subscription_name: str = Field(description="The name of the subscription that requested the prefilling queue")
    realms_topics: List[RealmTopic] = Field(
        description="A list of realm-topic combinations that this subscriber subscribes to, "
        'e.g. [{"realm": "udm", "topic": "users/user"}].'
    )
