# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import AuthPassword, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPassword):

    config_map_name = "release-name-provisioning-api"
    secret_name = "release-name-provisioning-api-admin"
    workload_name = "release-name-provisioning-api"

    sub_path_env_password = "env[?@name=='ADMIN_PASSWORD']"

    prefix_mapping = {
        "api.auth.admin": "provisioningApi.auth",
    }


class TestAuthRegisterConsumers(TestAuth):

    workload_kind = "Job"
    workload_name = "release-name-provisioning-register-consumers-1"
