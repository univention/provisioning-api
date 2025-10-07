# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class SettingsPrefillUdmSecret:
    secret_name = "release-name-provisioning-prefill-udm"
    prefix_mapping = {"prefill.udm.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='UDM_PASSWORD']"
    workload_name = "release-name-provisioning-prefill"


class TestChartCreatesPrefillUdmSecretAsUser(SettingsPrefillUdmSecret, AuthSecretGenerationUser):
    pass


class TestPrefillUsesPrefillUdmSecretByEnv(SettingsPrefillUdmSecret, AuthPasswordUsageViaEnv):
    pass


class TestPrefillInitContainerUsesUdmSecretViaEnv_WaitForUdm(SettingsPrefillUdmSecret, AuthPasswordUsageViaEnv):
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-udm']"
