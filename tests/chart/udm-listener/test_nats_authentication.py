# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser
from univention.testing.helm.auth_flavors.username import AuthUsernameViaEnv


class SettingsUdmListenerNatsSecret:
    secret_name = "release-name-udm-listener-nats"
    prefix_mapping = {
        "auth.user": "auth.username",
        "nats.auth": "auth",
    }

    # for AuthPasswordUsageViaEnv and AuthUsernameViaEnv
    workload_name = "release-name-udm-listener"
    workload_kind = "StatefulSet"
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    sub_path_env_username = "env[?@name=='NATS_USER']"
    default_username = "stub-username"


class TestChartCreatesUdmListenerNatsSecretAsUser(SettingsUdmListenerNatsSecret, AuthSecretGenerationUser):
    pass


class TestUdmListenerUsesNatsSecretViaEnv(SettingsUdmListenerNatsSecret, AuthPasswordUsageViaEnv):
    volume_name = "secret-nats"


class TestUdmListenerUsesNatsUsernameViaEnv(SettingsUdmListenerNatsSecret, AuthUsernameViaEnv):
    pass


class TestUdmListenerInitContainerUsesNatsSecretViaEnv_WaitForNats(
    SettingsUdmListenerNatsSecret, AuthPasswordUsageViaEnv
):
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-nats']"


class TestUdmListenerInitContainerUsesNatsUsernameViaEnv_WaitForNats(SettingsUdmListenerNatsSecret, AuthUsernameViaEnv):
    path_container = "..spec.template.spec.initContainers[?@.name=='wait-for-nats']"
