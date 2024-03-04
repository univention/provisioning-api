# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class PrefillSettings(BaseSettings):
    # Nats user name specific to Prefill Daemon
    nats_user: str
    # Nats password specific to Prefill Daemon
    nats_password: str

    # Prefill: username
    prefill_username: str
    # Prefill: password
    prefill_password: str

    # UDM REST API: host
    udm_host: str = "localhost"
    # UDM REST API: port
    udm_port: int = 9979
    # UDM REST API: username
    udm_username: str
    # UDM REST API: password
    udm_password: str

    @property
    def udm_url(self) -> str:
        return f"http://{self.udm_host}:{self.udm_port}/udm"


prefill_settings = PrefillSettings()
