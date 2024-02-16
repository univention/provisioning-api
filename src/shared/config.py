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

    # Nats: host
    nats_host: str = "localhost"
    # Nats: port
    nats_port: int = 4222
    # Nats: username
    nats_username: str = "nats"
    # Nats: password
    nats_password: str = "password"

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"

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

    # Internal REST API: host
    internal_api_host: str = "localhost"
    # Internal REST API: port
    internal_api_port: int = 7777
    # Internal REST API: username
    internal_api_username: str = ""
    # Internal REST API: password
    internal_api_password: str = ""

    @property
    def internal_api_url(self) -> str:
        return f"http://{self.internal_api_host}:{self.internal_api_port}/internal/v1"

    # Admin API: username
    admin_username: str = "admin"
    # Admin API: password
    admin_password: str = "password"

    # LDAP : port
    ldap_port: int = 389
    # LDAP : host
    ldap_host: str = "localhost"
    # LDAP : tls_mode
    tls_mode: str = "off"
    # LDAP : base_dn
    ldap_base_dn: str = "dc=univention-organization,dc=intranet"
    # LDAP : host_dn
    ldap_host_dn: str = "cn=admin,dc=univention-organization,dc=intranet"
    # LDAP : password
    ldap_password: str = "univention"

    @property
    def ldap_server_uri(self) -> str:
        return f"ldap://{self.ldap_host}:{self.ldap_port}"

    # TODO: define credentials for Dispatcher and Prefill

    # Dispatcher: username
    dispatcher_username: str = "dispatcher"
    # Dispatcher: password
    dispatcher_password: str = "password"

    # Prefill: username
    prefill_username: str = "prefill"
    # Prefill: password
    prefill_password: str = "password"

    # UDM Producer: username
    udm_producer_username: str = "udm_producer"
    # UDM Producer: password
    udm_producer_password: str = "password"


settings = Settings()
