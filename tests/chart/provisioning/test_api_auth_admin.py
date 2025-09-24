# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner


class TestAuth(AuthSecretGenerationOwner, AuthPasswordUsageViaEnv):
    secret_name = "release-name-provisioning-api-admin"
    workload_name = "release-name-provisioning-api"

    prefix_mapping = {
        "api.auth.admin": "auth",
    }
    sub_path_env_password = "env[?@name=='ADMIN_PASSWORD']"
    derived_password = "d487c3d05e836a952b600964eed58f7b0e60e99c"
