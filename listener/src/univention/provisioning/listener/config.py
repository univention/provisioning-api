# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from functools import lru_cache

from pydantic import BaseSettings

# SettingsSourceCallable = Callable[["BaseSettings"], Dict[str, Any]]
#
#
# def ucr_ldap_producer_settings(settings: BaseSettings) -> Dict[str, Any]:
#     try:
#         from univention.config_registry import ConfigRegistry
#     except ImportError:
#         return {}
#     ucr = ConfigRegistry()
#     ucr.load()
#
#     conf = {
#         "nats_user": ucr.get("nats/user", "univention"),
#         "nats_host": ucr.get("nats/host", "localhost"),
#         "nats_port": ucr.get("nats/port", 4222),
#         "nats_max_reconnect_attempts": ucr.get("nats/max_reconnect_attempts", 10),
#         "nats_retry_delay": ucr.get("nats/retry_delay", 10),
#         "nats_max_retry_count": ucr.get("nats/max_retry_count", 3),
#         "nats_password": "univention",
#     }
#
#     nats_password_file = ucr.get("nats/passwordfile", "/etc/nats/provisioning-listener.secret")
#
#     if os.path.exists(nats_password_file):
#         with open(nats_password_file, "r") as f:
#             conf["nats_password"] = f.read().strip()
#
#     return conf


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
    nats_retry_delay: int
    # Maximum number of retry attempts for interacting with the NATS server
    nats_max_retry_count: int

    # class Config:
    #     @classmethod
    #     def customise_sources(
    #         cls,
    #         init_settings: SettingsSourceCallable,
    #         file_secret_settings: SettingsSourceCallable,
    #         env_settings: SettingsSourceCallable,
    #     ) -> Tuple[SettingsSourceCallable, ...]:
    #         return (
    #             init_settings,
    #             ucr_ldap_producer_settings,
    #             file_secret_settings,
    #             env_settings,
    #         )

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"


# def ucr_nats_mq_settings(settings: BaseSettings) -> Dict[str, Any]:
#     try:
#         from univention.config_registry import ConfigRegistry
#     except ImportError:
#         return {}
#     ucr = ConfigRegistry()
#     ucr.load()
#
#     conf = {
#         "num_replicas": ucr.get("nats/num_replicas", 1),
#     }
#     return conf
#
#
# class NATSMQSettings(BaseSettings):
#     """
#     Settings for the NATS message queue.
#     """
#
#     num_replicas: int = 1
#
#     class Config:
#         @classmethod
#         def customise_sources(
#             cls,
#             init_settings: SettingsSourceCallable,
#             file_secret_settings: SettingsSourceCallable,
#             env_settings: SettingsSourceCallable,
#         ) -> Tuple[SettingsSourceCallable, ...]:
#             return (
#                 init_settings,
#                 ucr_nats_mq_settings,
#                 file_secret_settings,
#                 env_settings,
#             )
#
#
@lru_cache(maxsize=1)
def ldap_producer_settings() -> LdapProducerSettings:
    return LdapProducerSettings()


#
# @lru_cache(maxsize=1)
# def nats_mq_settings() -> NATSMQSettings:
#     return NATSMQSettings()
