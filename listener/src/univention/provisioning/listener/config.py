# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import os
from functools import lru_cache
from typing import Any, Callable, Dict, Tuple

from pydantic import BaseSettings, conint

SettingsSourceCallable = Callable[["BaseSettings"], Dict[str, Any]]


def ucr_ldap_producer_settings(settings: BaseSettings) -> Dict[str, Any]:
    try:
        from univention.config_registry import ConfigRegistry
    except ImportError:
        return {}
    ucr = ConfigRegistry()
    ucr.load()

    if "nats/user" not in ucr:
        return {}

    conf = {
        "log_level": ucr.get("provisioning-service/log/level", "INFO"),
        "nats_user": ucr.get("nats/user"),
        "nats_host": ucr.get("nats/host", "localhost"),
        "nats_port": ucr.get("nats/port", 4222),
        "nats_max_reconnect_attempts": ucr.get("nats/max_reconnect_attempts", 10),
        "nats_retry_delay": ucr.get("nats/retry_delay", 10),
        "nats_max_retry_count": ucr.get("nats/max_retry_count", 3),
        "terminate_listener_on_exception": ucr.get("nats/terminate_listener_on_exception", False),
    }

    nats_password_file = ucr.get("nats/passwordfile", "/etc/nats/provisioning-listener.secret")

    if os.path.exists(nats_password_file):
        with open(nats_password_file, "r") as f:
            conf["nats_password"] = f.read().strip()

    return conf


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

    class Config:
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                ucr_ldap_producer_settings,
                file_secret_settings,
                env_settings,
            )

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


@lru_cache(maxsize=1)
def ldap_producer_settings() -> LdapProducerSettings:
    return LdapProducerSettings()
