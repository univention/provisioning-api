# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import AuthPassword, AuthPasswordOwner, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPasswordOwner, AuthPassword):

    secret_name = "release-name-provisioning-api-prefill"
    workload_name = "release-name-provisioning-api"

    sub_path_env_password = "env[?@name=='PREFILL_PASSWORD']"

    derived_password = "e09fc522799483220870d968453b47bf12aa197c"

    prefix_mapping = {
        "api.auth.prefill": "provisioningApi.auth",
    }
