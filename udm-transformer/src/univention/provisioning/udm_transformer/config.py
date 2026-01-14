# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings

from univention.provisioning.models.constants import PublisherName

Loglevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class UDMTransformerSettings(BaseSettings):
    # Python log level
    log_level: Loglevel

    # Nats user name specific to UdmProducerSettings
    nats_user: str
    # Nats password specific to UdmProducerSettings
    nats_password: str
    # Nats: host
    nats_host: str
    # Nats: port
    nats_port: int
    # Enables toggling between `ldif-producer` and `udm-listener`
    ldap_publisher_name: PublisherName

    # Events API: username
    events_username_udm: str
    # Events API: password
    events_password_udm: str

    # UDM: host - example: https://primary.ucs.test/univention/udm/
    udm_url: str
    # UDM: username - ATTENTION: has to be allowed to use UDM REST API
    udm_username: str
    # UDM: password
    udm_password: str
    # UDM: needs reload - meaning: should reload UDM REST API on each extended_attributes change, used for Kubernetes only
    udm_needs_reload: bool = True

    # Provisioning REST API: host
    provisioning_api_host: str
    # Provisioning REST API: port
    provisioning_api_port: int

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"

    @property
    def provisioning_api_url(self) -> str:
        return f"http://{self.provisioning_api_host}:{self.provisioning_api_port}"


@lru_cache(maxsize=1)
def udm_transformer_settings() -> UDMTransformerSettings:
    return UDMTransformerSettings()
