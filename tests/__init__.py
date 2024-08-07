# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import os

ENV_DEFAULTS = {
    "admin_username": "admin",
    "admin_password": "provisioning",
    "udm_username": "cn=admin",
    "udm_password": "univention",
    "ldap_port": "389",
    "ldap_host": "ldap-server",
    "tls_mode": "off",
    "ldap_base_dn": "dc=univention-organization,dc=intranet",
    "ldap_host_dn": "cn=admin,dc=univention-organization,dc=intranet",
    "ldap_password": "univention",
    "nats_host": "foo",
    "nats_port": "1234",
    "nats_user": "api",
    "nats_password": "apipass",
    "admin_nats_user": "admin",
    "admin_nats_password": "nimda",
    "provisioning_api_base_url": "http://localhost:7777",
    "provisioning_api_username": "foo",
    "provisioning_api_password": "bar",
    "prefill_username": "prefill",
    "prefill_password": "prefillpass",
    "max_prefill_attempts": "10",
    "events_username_udm": "udm",
    "events_password_udm": "udmpass",
    "log_level": "DEBUG",
    "max_acknowledgement_retries": "3",
}


def set_test_env_vars():
    for var, default in ENV_DEFAULTS.items():
        if var.lower() in (key.lower() for key in os.environ):
            continue
        os.environ[var] = default
        print(f"{var} was not explicitly set, setting the following default: {default}")
