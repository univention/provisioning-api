# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class DispatcherSettings(BaseSettings):
    # Nats user name specific to Dispatcher
    nats_user: str
    # Nats password specific to Dispatcher
    nats_password: str
