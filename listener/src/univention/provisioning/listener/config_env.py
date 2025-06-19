# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from functools import lru_cache

from pydantic import conint
from pydantic_settings import BaseSettings


class LdapProducerSettings(BaseSettings):
    # Nats user name specific to UdmProducerSettings
    nats_user: str
    # Nats password specific to UdmProducerSettings
    nats_password: str
    # Nats: host
    nats_host: str
    # Nats: port
    nats_port: int
    # Maximum number of reconnect attempts to the NATS server
    nats_max_reconnect_attempts: int
    # Delay between retry attempts to the NATS server (in seconds)
    nats_retry_delay: conint(ge=0)
    # Maximum number of retry attempts for interacting with the NATS server
    nats_max_retry_count: conint(ge=0)
    # Enable termination on NATS failure
    terminate_listener_on_exception: bool

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


class NATSMQSettings(BaseSettings):
    """
    Settings for the NATS message queue.
    """

    num_replicas: int = 1


@lru_cache(maxsize=1)
def ldap_producer_settings() -> LdapProducerSettings:
    return LdapProducerSettings()
