# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import os
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
    # Delay between retry attempts to the NATS server (in seconds)
    nats_retry_delay: int
    # Maximum number of retry attempts for interacting with the NATS server
    nats_max_retry_count: int

    def __init__(self):
        ucr = ConfigRegistry()
        ucr.load()
        self.nats_user = ucr.get("nats/user", "univention")
        self.nats_password_file = ucr.get("nats/passwordfile", "/etc/nats/provisioning-listener.secret")
        self.nats_host = ucr.get("nats/host", "localhost")
        self.nats_port = ucr.get("nats/port", 4222)
        self.nats_max_reconnect_attempts = ucr.get("nats/max_reconnect_attempts", 10)
        self.nats_retry_delay = ucr.get("nats/retry_delay", 10)
        self.nats_max_retry_count = ucr.get("nats/max_retry_count", 3)
        if os.path.exists(self.nats_password_file):
            with open(self.nats_password_file, "r") as f:
                self.nats_password = f.read().strip()

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
