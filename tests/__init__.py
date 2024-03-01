# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import os


def set_test_env_vars():
    os.environ["admin_username"] = "admin"
    os.environ["admin_password"] = "provisioning"
    os.environ["udm_username"] = "cn=admin"
    os.environ["udm_password"] = "univention"
    os.environ["ldap_port"] = "389"
    os.environ["ldap_host"] = "ldap-server"
    os.environ["tls_mode"] = "off"
    os.environ["ldap_base_dn"] = "dc=univention-organization,dc=intranet"
    os.environ["ldap_host_dn"] = "cn=admin,dc=univention-organization,dc=intranet"
    os.environ["ldap_password"] = "univention"
    os.environ["nats_user"] = "api"
    os.environ["nats_password"] = "apipass"
    os.environ["admin_nats_user"] = "admin"
    os.environ["admin_nats_password"] = "nimda"
