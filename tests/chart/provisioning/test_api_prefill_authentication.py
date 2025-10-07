# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner


class SettingsTestProvisioningApiPrefillSecret:
    secret_name = "release-name-provisioning-api-prefill"
    prefix_mapping = {"api.auth.prefill": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='PREFILL_PASSWORD']"


class TestChartCreatesProvisioningApiPrefillSecretAsOwner(
    SettingsTestProvisioningApiPrefillSecret, AuthSecretGenerationOwner
):
    derived_password = "6f0bc322c483ff43630e2e73e51047748dd693d7"


class TestPrefillAndConsumerApiUsesProvisioningApiPrefillSecretByEnv(
    SettingsTestProvisioningApiPrefillSecret, AuthPasswordUsageViaEnv
):
    workload_name = "release-name-provisioning-api"


class TestPrefillUsesProvisioningApiPrefillSecretByEnv(
    SettingsTestProvisioningApiPrefillSecret, AuthPasswordUsageViaEnv
):
    workload_name = "release-name-provisioning-prefill"
