# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv


class TestAuth(AuthPasswordUsageViaEnv):
    secret_name = "release-name-provisioning-api-admin"
    workload_kind = "Job"
    workload_name = "release-name-provisioning-register-consumers-1"

    sub_path_env_password = "env[?@name=='ADMIN_PASSWORD']"

    prefix_mapping = {
        "api.auth.admin": "auth",
    }
