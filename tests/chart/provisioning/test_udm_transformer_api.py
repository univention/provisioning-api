# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv


class TestAuth(AuthPasswordUsageViaEnv):
    secret_name = "release-name-provisioning-api-events"
    workload_name = "release-name-provisioning-udm-transformer"

    sub_path_env_password = "env[?@name=='EVENTS_PASSWORD_UDM']"

    prefix_mapping = {
        "api.auth.eventsUdm": "auth",
    }
