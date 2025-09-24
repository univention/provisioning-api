# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner


class TestAuth(AuthSecretGenerationOwner, AuthPasswordUsageViaEnv):
    workload_kind = "StatefulSet"
    workload_name = "release-name-udm-listener"
    secret_name = "release-name-udm-listener-nats"

    prefix_mapping = {
        "nats.auth": "auth",
    }
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    derived_password = "c4bcaffc26984205d02265dd6c1894d7ad6e9d45"
