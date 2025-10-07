# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class SettingsTestDispatcherNatsSecret:
    secret_name = "release-name-provisioning-dispatcher-nats"
    prefix_mapping = {"dispatcher.nats.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    workload_name = "release-name-provisioning-dispatcher"


class TestChartCreatesDispatcherNatsSecretAsUser(SettingsTestDispatcherNatsSecret, AuthSecretGenerationUser):
    pass


class TestDispatcherApiUsesProvisioningApiNatsSecretByEnv(SettingsTestDispatcherNatsSecret, AuthPasswordUsageViaEnv):
    pass


class TestDispatcherApiInitContainerUsesNatsSecretViaEnv_WaitForNats(
    SettingsTestDispatcherNatsSecret, AuthPasswordUsageViaEnv
):
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-nats']"
