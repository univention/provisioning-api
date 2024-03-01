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

    # Admin Nats user name
    admin_nats_user: str
    # Admin Nats password
    admin_nats_password: str

    # Dispatcher: username
    dispatcher_username: str
    # Dispatcher: password
    dispatcher_password: str

    # Prefill: username
    prefill_username: str
    # Prefill: password
    prefill_password: str

    # UDM Producer: username
    udm_listener_username: str
    # UDM Producer: password
    udm_listener_password: str


app_settings = AppSettings()
