# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    log_level: Loglevel = "INFO"
    provisioning_api_base_url: str
    provisioning_api_username: str
    provisioning_api_password: str

    udm_url: str
    udm_username: str
    udm_password: str

    kubernetes_namespace: str


@lru_cache(maxsize=1)
def settings() -> Settings:
    return Settings()
