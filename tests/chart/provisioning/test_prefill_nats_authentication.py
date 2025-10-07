# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationUser


class SettingsPrefillNatsSecret:
    secret_name = "release-name-provisioning-prefill-nats"
    prefix_mapping = {"prefill.nats.auth": "auth"}

    # for AuthPasswordUsageViaEnv
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    workload_name = "release-name-provisioning-prefill"


class TestChartCreatesPrefillNatsSecretAsUser(SettingsPrefillNatsSecret, AuthSecretGenerationUser):
    pass


class TestPrefillUsesPrefillNatsSecretByEnv(SettingsPrefillNatsSecret, AuthPasswordUsageViaEnv):
    pass
