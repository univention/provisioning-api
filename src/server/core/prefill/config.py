# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from functools import lru_cache

from pydantic import conint
from pydantic_settings import BaseSettings


class PrefillSettings(BaseSettings):
    # Python log level
    log_level: str = "INFO"

    # Nats user name specific to Prefill Daemon
    nats_user: str
    # Nats password specific to Prefill Daemon
    nats_password: str
    # Nats: host
    nats_host: str
    # Nats: port
    nats_port: int

    # Prefill: username
    prefill_username: str
    # Prefill: password
    prefill_password: str
    # Prefill: maximum number of retries of a prefill request
    # -1 means infinite retries.
    max_prefill_attempts: conint(ge=-1)

    # UDM REST API: host
    udm_host: str = "localhost"
    # UDM REST API: port
    udm_port: int = 9979
    # UDM REST API: username
    udm_username: str
    # UDM REST API: password
    udm_password: str
    # Maximum number of reconnect attempts to the NATS server
    max_reconnect_attempts: conint(ge=0) = 5

    # Provisioning REST API: host
    provisioning_api_host: str = "localhost"
    # Provisioning REST API: port
    provisioning_api_port: int = 7777

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"

    @property
    def udm_url(self) -> str:
        return f"http://{self.udm_host}:{self.udm_port}/udm"

    @property
    def provisioning_api_url(self) -> str:
        return f"http://{self.provisioning_api_host}:{self.provisioning_api_port}"


@lru_cache(maxsize=1)
def get_prefill_settings() -> PrefillSettings:
    return PrefillSettings()
