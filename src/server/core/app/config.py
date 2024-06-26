# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    # Admin API: username
    admin_username: str
    # Admin API: password
    admin_password: str

    # Nats user name specific to Consumer and Internal API
    nats_user: str
    # Nats password specific to Consumer and Internal API
    nats_password: str
    # Nats: host
    nats_host: str
    # Nats: port
    nats_port: int
    # Admin Nats user name
    admin_nats_user: str
    # Admin Nats password
    admin_nats_password: str

    # Prefill: username
    prefill_username: str
    # Prefill: password
    prefill_password: str

    # Events API: username
    events_username_udm: str
    # Events API: password
    events_password_udm: str

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


app_settings = AppSettings()
