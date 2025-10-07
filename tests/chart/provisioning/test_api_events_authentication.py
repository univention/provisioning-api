# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner


class SettingsTestProvisioningApiEventsSecret:
    secret_name = "release-name-provisioning-api-events"
    prefix_mapping = {"api.auth.eventsUdm": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='EVENTS_PASSWORD_UDM']"


class TestChartCreatesProvisioningApiEventsSecretAsOwner(
    SettingsTestProvisioningApiEventsSecret, AuthSecretGenerationOwner
):
    derived_password = "1eb76a52da9cfffbcf8eb07dbc105844c3e06c26"


class TestEventsAndConsumerApiUsesProvisioningApiEventsSecretByEnv(
    SettingsTestProvisioningApiEventsSecret, AuthPasswordUsageViaEnv
):
    workload_name = "release-name-provisioning-api"


class TestUdmTransformerUsesProvisioningApiEventsSecretByEnv(
    SettingsTestProvisioningApiEventsSecret, AuthPasswordUsageViaEnv
):
    workload_name = "release-name-provisioning-udm-transformer"
