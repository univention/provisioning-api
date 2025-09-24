# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class TestAuth(AuthSecretGenerationUser, AuthPasswordUsageViaEnv):
    config_map_name = "release-name-provisioning-register-consumers"
    secret_name = "release-name-provisioning-register-consumers-udm"
    workload_kind = "Job"

    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-data-loader']"

    prefix_mapping = {
        "registerConsumers.udm.auth": "auth",
    }
    sub_path_env_password = "env[?@name=='UDM_PASSWORD']"
