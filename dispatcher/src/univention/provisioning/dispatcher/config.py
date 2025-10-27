# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from functools import lru_cache
from typing import Literal

from pydantic import ValidationError
from pydantic_settings import BaseSettings

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class BaseDispatcherSettings(BaseSettings):
    # Python log level
    log_level: Loglevel
    # Maximum number of reconnect attempts to the NATS server
    nats_max_reconnect_attempts: int


class DispatcherSettings(BaseDispatcherSettings):
    # Nats user name specific to Dispatcher
    nats_user: str
    # Nats password specific to Dispatcher
    nats_password: str
    # Nats: host
    nats_host: str
    # Nats: port
    nats_port: int

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


class DispatcherSettingsPull(BaseDispatcherSettings):
    # Nats user name specific to Dispatcher
    nats_user_pull: str
    # Nats password specific to Dispatcher
    nats_password_pull: str
    # Nats: host
    nats_host_pull: str
    # Nats: port
    nats_port_pull: int

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host_pull}:{self.nats_port_pull}"

    @property
    def nats_user(self) -> str:
        return self.nats_user_pull

    @property
    def nats_password(self) -> str:
        return self.nats_password_pull

    @property
    def nats_host(self) -> str:
        return self.nats_host_pull

    @property
    def nats_port(self) -> int:
        return self.nats_port_pull


class DispatcherSettingsPush(BaseDispatcherSettings):
    # Nats user name specific to Dispatcher
    nats_user_push: str
    # Nats password specific to Dispatcher
    nats_password_push: str
    # Nats: host
    nats_host_push: str
    # Nats: port
    nats_port_push: int

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host_push}:{self.nats_port_push}"

    @property
    def nats_user(self) -> str:
        return self.nats_user_push

    @property
    def nats_password(self) -> str:
        return self.nats_password_push

    @property
    def nats_host(self) -> str:
        return self.nats_host_push

    @property
    def nats_port(self) -> int:
        return self.nats_port_push


@lru_cache(maxsize=1)
def dispatcher_settings_pull() -> BaseDispatcherSettings:
    try:
        return DispatcherSettingsPull()
    except ValidationError:
        return DispatcherSettings()


@lru_cache(maxsize=1)
def dispatcher_settings_push() -> BaseDispatcherSettings:
    try:
        return DispatcherSettingsPush()
    except ValidationError:
        return DispatcherSettings()


@lru_cache(maxsize=1)
def dispatcher_settings() -> BaseDispatcherSettings:
    return DispatcherSettings()
