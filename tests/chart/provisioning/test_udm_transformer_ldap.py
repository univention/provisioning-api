# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class TestAuth(AuthSecretGenerationUser, AuthPasswordUsageViaEnv):
    config_map_name = "release-name-provisioning-udm-transformer"
    secret_name = "release-name-provisioning-udm-transformer-ldap"
    workload_name = "release-name-provisioning-udm-transformer"

    path_ldap_bind_dn = "data.LDAP_BIND_DN"

    sub_path_env_password = "env[?@.name=='LDAP_BIND_PW']"

    prefix_mapping = {
        "udmTransformer.ldap.auth": "auth",
    }
