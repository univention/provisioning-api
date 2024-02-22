# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class UdmMessagingSettings(BaseSettings):
    # Nats user name specific to UdmMessaging
    nats_user: str = "udmmessaging"
    # Nats password specific to UdmMessaging
    nats_password: str = "udmmessagingpass"


settings = UdmMessagingSettings()
