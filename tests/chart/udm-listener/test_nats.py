# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

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
    derived_password = "nbs_c4bcaffc26984205d02265dd6c1894d7ad6e9d45"

    @pytest.mark.skip(reason="Chart doesn't use nubus-common password generation")
    def test_auth_password_has_random_value(self, chart):
        pass
