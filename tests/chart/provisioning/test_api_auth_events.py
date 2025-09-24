# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import AuthPassword, AuthPasswordOwner, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPasswordOwner, AuthPassword):
    is_secret_owner = True
    secret_name = "release-name-provisioning-api-events"
    workload_name = "release-name-provisioning-api"

    sub_path_env_password = "env[?@name=='EVENTS_PASSWORD_UDM']"

    derived_password = "1eb76a52da9cfffbcf8eb07dbc105844c3e06c26"

    prefix_mapping = {
        "api.auth.eventsUdm": "provisioningApi.auth",
    }
