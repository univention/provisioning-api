# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Literal

from pydantic import conint
from pydantic_settings import BaseSettings

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ProvisioningConsumerClientSettings(BaseSettings):
    provisioning_api_base_url: str
    provisioning_api_username: str
    provisioning_api_password: str
    log_level: Loglevel = "INFO"

    @property
    def consumer_registration_url(self) -> str:
        return f"{self.provisioning_api_base_url}/subscriptions/v1"

    @property
    def consumer_messages_url(self) -> str:
        return f"{self.provisioning_api_base_url}/messages/v1"


class MessageHandlerSettings(BaseSettings):
    max_acknowledgement_retries: conint(ge=0, le=10)
