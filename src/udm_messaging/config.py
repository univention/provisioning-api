# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class UdmProducerSettings(BaseSettings):
    # Nats user name specific to UdmProducerSettings
    nats_user: str
    # Nats password specific to UdmProducerSettings
    nats_password: str

    # Events API: username
    events_username_udm: str
    # Events API: password
    events_password_udm: str

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
    ldap_password: str

    @property
    def ldap_server_uri(self) -> str:
        return f"ldap://{self.ldap_host}:{self.ldap_port}"


udm_producer_settings = UdmProducerSettings()
