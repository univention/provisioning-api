# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaVolume
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class TestAuth(AuthSecretGenerationUser, AuthPasswordUsageViaVolume):
    config_map_name = "release-name-udm-listener"
    secret_name = "release-name-udm-listener-ldap"
    workload_kind = "StatefulSet"
    workload_name = "release-name-udm-listener"

    prefix_mapping = {
        "ldap.auth": "auth",
    }

    volume_name = "secret-ldap"
