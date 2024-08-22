# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from functools import lru_cache

from pydantic_settings import BaseSettings


class DispatcherSettings(BaseSettings):
    # Python log level
    log_level: str = "INFO"

    # Nats user name specific to Dispatcher
    nats_user: str
    # Nats password specific to Dispatcher
    nats_password: str
    # Nats: host
    nats_host: str
    # Nats: port
    nats_port: int
    # Maximum number of reconnect attempts to the NATS server
    max_reconnect_attempts: int = 5

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


@lru_cache
def get_dispatcher_settings() -> DispatcherSettings:
    return DispatcherSettings()
