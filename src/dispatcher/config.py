# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class DispatcherSettings(BaseSettings):
    # Nats user name specific to Dispatcher
    nats_user: str
    # Nats password specific to Dispatcher
    nats_password: str
    # Maximum number of reconnect attempts to the NATS server
    max_reconnect_attempts: int = 5

    # FIXME: should we get rid of these fields?
    # Dispatcher: username
    dispatcher_username: str
    # Dispatcher: password
    dispatcher_password: str


dispatcher_settings = DispatcherSettings()
