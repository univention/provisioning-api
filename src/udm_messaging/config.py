# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class LdapSettings(BaseSettings):
    # LDAP : port
    ldap_port: int
    # LDAP : host
    ldap_host: str
    # LDAP : tls_mode
    tls_mode: str
    # LDAP : base_dn
    ldap_base_dn: str
    # LDAP : host_dn
    ldap_host_dn: str
    # LDAP : password
    ldap_password: str

    @property
    def ldap_server_uri(self) -> str:
        return f"ldap://{self.ldap_host}:{self.ldap_port}"


ldap_settings = LdapSettings()
