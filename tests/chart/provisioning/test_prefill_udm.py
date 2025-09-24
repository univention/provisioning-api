# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class Config:
    secret_name = "release-name-provisioning-prefill-udm"
    workload_name = "release-name-provisioning-prefill"

    prefix_mapping = {
        "prefill.udm.auth": "auth",
    }
    sub_path_env_password = "env[?@name=='UDM_PASSWORD']"


class TestAuth(Config, AuthSecretGenerationUser, AuthPasswordUsageViaEnv):
    config_map_name = "release-name-provisioning-prefill"


class TestAuthWaitForUdm(Config, AuthSecretGenerationUser, AuthPasswordUsageViaEnv):
    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-udm']"
