# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import AuthPassword, AuthPasswordOwner, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPasswordOwner, AuthPassword):
    secret_name = "release-name-provisioning-api-admin"
    workload_name = "release-name-provisioning-api"

    sub_path_env_password = "env[?@name=='ADMIN_PASSWORD']"

    derived_password = "d487c3d05e836a952b600964eed58f7b0e60e99c"

    prefix_mapping = {
        "api.auth.admin": "provisioningApi.auth",
    }
