# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class SettingsUdmTransformerLdapSecret:
    secret_name = "release-name-provisioning-udm-rest-api-udm-transformer"
    prefix_mapping = {"udmTransformer.udm.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='UDM_PASSWORD']"
    workload_name = "release-name-provisioning-udm-transformer"


class TestChartCreatesUdmTransformerLdapSecretAsUser(SettingsUdmTransformerLdapSecret, AuthSecretGenerationUser):
    pass


class TestUdmTransformerUsesLdapSecretViaEnv(SettingsUdmTransformerLdapSecret, AuthPasswordUsageViaEnv):
    pass


class TestUdmTransformerInitContainerUsesUdmSecretViaEnv_WaitForUdm(
    SettingsUdmTransformerLdapSecret, AuthPasswordUsageViaEnv
):
    sub_path_env_password = "env[?@name=='UDM_API_PASSWORD']"
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-udm']"
