# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Tuple
from pydantic_settings import BaseSettings
import uuid


class Settings(BaseSettings):
    subscription_name: str = str(uuid.uuid4())

    provisioning_api_base_url: str
    provisioning_api_username: str
    provisioning_api_password: str

    realms_topics: List[Tuple[str, str]]
    request_prefill: bool

    @property
    def consumer_registration_url(self) -> str:
        return f"{self.provisioning_api_base_url}/subscriptions/v1"

    @property
    def consumer_messages_url(self) -> str:
        return f"{self.provisioning_api_base_url}/messages/v1"
