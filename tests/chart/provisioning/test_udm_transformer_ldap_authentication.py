# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser
from univention.testing.helm.auth_flavors.username import AuthUsernameViaConfigMap


class SettingsUdmTransformerLdapSecret:
    secret_name = "release-name-provisioning-udm-transformer-ldap"
    prefix_mapping = {"auth.bindDn": "auth.username", "udmTransformer.ldap.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='LDAP_BIND_PW']"
    workload_name = "release-name-provisioning-udm-transformer"


class TestChartCreatesUdmTransformerLdapSecretAsUser(SettingsUdmTransformerLdapSecret, AuthSecretGenerationUser):
    pass


class TestUdmTransformerUsesLdapSecretViaEnv(SettingsUdmTransformerLdapSecret, AuthPasswordUsageViaEnv):
    pass


class TestUdmTransformerUsesLdapUsernameViaConfigMap(SettingsUdmTransformerLdapSecret, AuthUsernameViaConfigMap):
    config_map_name = "release-name-provisioning-udm-transformer"
    path_username = "data.LDAP_BIND_DN"
    default_username = "cn=admin,dc=univention-organization,dc=intranet"
