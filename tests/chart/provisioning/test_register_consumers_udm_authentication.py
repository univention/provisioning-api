# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class SettingsRegisterConsumersUdmSecret:
    secret_name = "release-name-provisioning-register-consumers-udm"
    prefix_mapping = {"registerConsumers.udm.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='UDM_PASSWORD']"
    workload_name = "release-name-provisioning-register-consumers-1"


class TestChartCreatesRegisterConsumersUdmSecretAsUser(SettingsRegisterConsumersUdmSecret, AuthSecretGenerationUser):
    pass


class TestRegisterConsumersInitContainerUsesUdmSecretViaEnv_WaitForDataLoader(
    SettingsRegisterConsumersUdmSecret, AuthPasswordUsageViaEnv
):
    workload_kind = "Job"
    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-data-loader']"
