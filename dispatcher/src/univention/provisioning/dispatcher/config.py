# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from functools import lru_cache
from typing import Literal

from pydantic import ConfigDict, ValidationError
from pydantic_settings import BaseSettings

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class DispatcherSettings(BaseSettings):
    # Python log level
    log_level: Loglevel

    # Nats user name specific to Dispatcher
    nats_user: str
    # Nats password specific to Dispatcher
    nats_password: str
    # Nats: host
    nats_host: str
    # Nats: port
    nats_port: int
    # Maximum number of reconnect attempts to the NATS server
    nats_max_reconnect_attempts: int = 2

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


class DispatcherSettingsPull(DispatcherSettings):
    model_config = ConfigDict(env_prefix="", env_suffix="_PULL")


class DispatcherSettingsPush(DispatcherSettings):
    model_config = ConfigDict(env_prefix="", env_suffix="_PUSH")


@lru_cache(maxsize=1)
def dispatcher_settings_pull() -> DispatcherSettings:
    try:
        return DispatcherSettingsPull()
    except ValidationError:
        return DispatcherSettings()


@lru_cache(maxsize=1)
def dispatcher_settings_push() -> DispatcherSettings:
    try:
        return DispatcherSettingsPush()
    except ValidationError:
        return DispatcherSettings()

@lru_cache(maxsize=1)
def dispatcher_settings() -> DispatcherSettings:
    return DispatcherSettings()