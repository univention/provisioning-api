# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import AuthPassword, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPassword):

    is_secret_owner = True

    secret_name = "release-name-provisioning-api"
    workload_kind = "Job"
    workload_name = "release-name-provisioning-register-consumers-1"

    path_password = "stringData.admin_password"

    sub_path_env_password = "env[?@name=='ADMIN_PASSWORD']"

    prefix_mapping = {
        "api.auth.admin": "provisioningApi.auth",
    }
