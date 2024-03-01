# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class EventsSettings(BaseSettings):
    # Nats user name specific to Events API
    nats_user: str
    # Nats password specific to Events API
    nats_password: str
