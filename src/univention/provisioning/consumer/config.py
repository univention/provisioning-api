# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from functools import cached_property
from typing import Literal
from urllib.parse import urljoin

from pydantic import conint
from pydantic_settings import BaseSettings

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ProvisioningConsumerClientSettings(BaseSettings):
    provisioning_api_base_url: str
    provisioning_api_username: str
    provisioning_api_password: str
    log_level: Loglevel = "INFO"

    @cached_property
    def subscriptions_url(self) -> str:
        return urljoin(self.provisioning_api_base_url, "/v1/subscriptions")

    def subscriptions_messages_url(self, name: str) -> str:
        return f"{self.subscriptions_url}/{name}/messages"

    @cached_property
    def messages_url(self) -> str:
        return urljoin(self.provisioning_api_base_url, "/v1/messages")


class MessageHandlerSettings(BaseSettings):
    max_acknowledgement_retries: conint(ge=0, le=10)
