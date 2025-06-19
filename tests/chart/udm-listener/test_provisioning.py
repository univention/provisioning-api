# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import Auth, SecretViaEnv, UsernameViaEnv


class TestAuth(SecretViaEnv, UsernameViaEnv, Auth):
    config_map_name = "release-name-udm-listener"
    secret_name = "release-name-udm-listener-provisioning-api"
    workload_kind = "StatefulSet"

    default_username = "udm"
    derived_password = "xxfe3b23688cf102b8936a82bcbcd4c4abf8d43d80"

    sub_path_env_password = "env[?@name=='EVENTS_PASSWORD_UDM']"
    sub_path_env_username = "env[?@name=='EVENTS_USERNAME_UDM']"
