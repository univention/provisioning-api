# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List
from pydantic_settings import BaseSettings
import uuid


class Settings(BaseSettings):
    # Consumer Name
    consumer_name: str = str(uuid.uuid4())

    # Provisioning API: host
    provisioning_api_host: str = "localhost"
    # Provisioning API: port
    provisioning_api_port: int = 7777
    # Provisioning API: username
    provisioning_api_username: str = ""
    # Provisioning REST API: password
    provisioning_api_password: str = ""

    realms_topics: List = []
    request_prefill: bool = False

    @property
    def base_url(self) -> str:
        return f"http://{self.provisioning_api_host}:{self.provisioning_api_port}"

    @property
    def consumer_registration_url(self) -> str:
        return f"{self.base_url}/subscriptions/v1"

    @property
    def consumer_messages_url(self) -> str:
        return f"{self.base_url}/messages/v1"


settings = Settings()