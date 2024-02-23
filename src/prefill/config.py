# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class PrefillSettings(BaseSettings):
    # Nats user name specific to Prefill Daemon
    nats_user: str
    # Nats password specific to Prefill Daemon
    nats_password: str
