# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import AuthPassword, AuthPasswordOwner, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPasswordOwner, AuthPassword):

    secret_name = "release-name-provisioning-api-events"
    workload_name = "release-name-provisioning-api"

    sub_path_env_password = "env[?@name=='EVENTS_PASSWORD_UDM']"

    derived_password = "c3fc1b2cc371b5b55b77c6f2d18a7674df530c5b"

    prefix_mapping = {
        "api.auth.eventsUdm": "provisioningApi.auth",
    }
