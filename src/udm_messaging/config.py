# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class UdmMessagingSettings(BaseSettings):
    # Nats user name specific to UdmMessaging
    nats_user: str
    # Nats password specific to UdmMessaging
    nats_password: str

    # UDM Producer: username
    username: str
    # UDM Producer: password
    password: str

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


udm_messaging_settings = UdmMessagingSettings()
