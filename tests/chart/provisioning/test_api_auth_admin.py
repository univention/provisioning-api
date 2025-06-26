# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import AuthPassword, AuthPasswordOwner, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPasswordOwner, AuthPassword):

    secret_name = "release-name-provisioning-api"
    workload_name = "release-name-provisioning-api"

    sub_path_env_password = "env[?@name=='ADMIN_PASSWORD']"

    path_password = "stringData.admin_password"

    derived_password = "751120bf3b933a18b7d637bfba5e9389939c4bbd"

    prefix_mapping = {
        "api.auth.admin": "provisioningApi.auth",
    }
