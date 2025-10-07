# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class SettingsTestUdmTransformerNatsSecret:
    secret_name = "release-name-provisioning-nats-udm-transformer"
    prefix_mapping = {"udmTransformer.nats.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    workload_name = "release-name-provisioning-udm-transformer"


class TestChartCreatesUdmTransformerNatsSecretAsUser(SettingsTestUdmTransformerNatsSecret, AuthSecretGenerationUser):
    pass


class TestUdmTransformerUsesNatsSecretByEnv(SettingsTestUdmTransformerNatsSecret, AuthPasswordUsageViaEnv):
    pass


class TestUdmTransformerInitContainerUsesNatsSecretViaEnv_WaitForNats(
    SettingsTestUdmTransformerNatsSecret, AuthPasswordUsageViaEnv
):
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-nats']"
