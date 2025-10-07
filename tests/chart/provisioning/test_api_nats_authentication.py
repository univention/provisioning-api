# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class SettingsTestProvisioningApiNatsSecret:
    secret_name = "release-name-provisioning-api-nats"
    prefix_mapping = {"api.nats.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    workload_name = "release-name-provisioning-api"


class TestChartCreatesProvisioningApiNatsSecretAsUser(SettingsTestProvisioningApiNatsSecret, AuthSecretGenerationUser):
    pass


class TestEventsAndConsumerApiUsesProvisioningApiNatsSecretByEnv(
    SettingsTestProvisioningApiNatsSecret, AuthPasswordUsageViaEnv
):
    pass


class TestEventsAndConsumerApiInitContainerUsesNatsSecretViaEnv_WaitForNats(
    SettingsTestProvisioningApiNatsSecret, AuthPasswordUsageViaEnv
):
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-nats']"
