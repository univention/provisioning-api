# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaVolume
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser
from univention.testing.helm.auth_flavors.username import AuthUsernameViaConfigMap


class SettingsUdmListenerLdapSecret:
    secret_name = "release-name-udm-listener-ldap"
    prefix_mapping = {
        "auth.bindDn": "auth.username",
        "ldap.auth": "auth",
    }

    # for AuthPasswordUsageViaVolume
    workload_name = "release-name-udm-listener"
    workload_kind = "StatefulSet"


class TestChartCreatesUdmListenerLdapSecretAsUser(SettingsUdmListenerLdapSecret, AuthSecretGenerationUser):
    pass


class TestUdmListenerUsesLdapSecretViaVolume(SettingsUdmListenerLdapSecret, AuthPasswordUsageViaVolume):
    volume_name = "secret-ldap"


class TestUdmListenerUsesLdapUsernameViaConfigMap(SettingsUdmListenerLdapSecret, AuthUsernameViaConfigMap):
    config_map_name = "release-name-udm-listener"
    path_username = "data.LDAP_HOST_DN"
    default_username = "cn=admin,dc=univention-organization,dc=intranet"
