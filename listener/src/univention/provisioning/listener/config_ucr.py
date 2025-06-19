# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from functools import lru_cache

from univention.config_registry import ConfigRegistry


class LdapProducerSettings:
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

    def __init__(self):
        self.nats_user = ConfigRegistry().get("nats/user", "univention")
        self.nats_password = ConfigRegistry().get("nats/password", "univention")
        self.nats_host = ConfigRegistry().get("nats/host", "localhost")
        self.nats_port = ConfigRegistry().get("nats/port", 4222)
        self.nats_max_reconnect_attempts = ConfigRegistry().get("nats/max_reconnect_attempts", 10)

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


class NATSMQSettings:
    """
    Settings for the NATS message queue.
    """
    num_replicas: int = 1

    def __init__(self):
        self.num_replicas = ConfigRegistry().get("nats/mq/num_replicas", 1)

@lru_cache(maxsize=1)
def ldap_producer_settings() -> LdapProducerSettings:
    return LdapProducerSettings()
