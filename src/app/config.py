# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    # Admin API: username
    admin_username: str
    # Admin API: password
    admin_password: str

    # Nats user name specific to Consumer and Internal API
    admin_nats_user: str
    # Nats password specific to Consumer and Internal API
    admin_nats_password: str


app_settings = AppSettings()
