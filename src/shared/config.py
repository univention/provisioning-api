# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Python log level
    log_level: str = "INFO"

    # FastAPI: debug mode
    debug: bool = True
    # FastAPI: webserver root path
    root_path: str = ""
    # FastAPI: disable CORS checks
    cors_all: bool = False

    # Redis: host
    redis_host: str = "localhost"
    # Redis: port
    redis_port: int = 6379

    # Nats: host
    nats_host: str = "localhost"
    # Nats: port
    nats_port: int = 4222

    # UDM REST API: host
    udm_host: str = "localhost"
    # UDM REST API: port
    udm_port: int = 9979
    # UDM REST API: username
    udm_username: str = "cn=admin"
    # UDM REST API: password
    udm_password: str = "univention"

    @property
    def udm_url(self) -> str:
        return f"http://{self.udm_host}:{self.udm_port}/udm"

    # Consumer and Event REST API: host
    consumer_event_host: str = "localhost"
    # Consumer and Event REST API: port
    consumer_event_port: int = 7777
    # Consumer and Event REST API: username
    consumer_event_username: str = ""
    # Consumer and Event REST API: password
    consumer_event_password: str = ""

    @property
    def event_url(self) -> str:
        return f"http://{self.host}:{self.consumer_event_port}/events/v1"

    @property
    def consumer_reg_url(self) -> str:
        return f"http://{self.host}:{self.consumer_event_port}/subscriptions/v1"

    # LDAP : port
    ldap_port: int = 389
    # LDAP : start_tls
    ldap_start_tls: int = 0
    # LDAP : base_dn
    ldap_base_dn: str = "dc=univention-organization,dc=intranet"
    # LDAP : host_dn
    ldap_host_dn: str = "cn=admin,dc=univention-organization,dc=intranet"
    # LDAP : password
    ldap_password: str = "univention"


settings = Settings()
