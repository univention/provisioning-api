# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Tuple
from pydantic_settings import BaseSettings
import uuid


class ClientSettings(BaseSettings):
    # Consumer Name
    consumer_name: str = str(uuid.uuid4())

    # Provisioning API URL
    provisioning_api_url: str
    # Provisioning API: username
    provisioning_api_username: str
    # Provisioning REST API: password
    provisioning_api_password: str

    realms_topics: List[Tuple[str, str]] = []
    request_prefill: bool = False

    @property
    def consumer_registration_url(self) -> str:
        return f"{self.provisioning_api_url}/subscriptions/v1"

    @property
    def consumer_messages_url(self) -> str:
        return f"{self.provisioning_api_url}/messages/v1"
