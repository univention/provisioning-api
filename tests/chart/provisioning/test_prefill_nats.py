# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner


class TestAuth(AuthSecretGenerationOwner, AuthPasswordUsageViaEnv):
    workload_name = "release-name-provisioning-prefill"
    secret_name = "release-name-provisioning-nats-prefill"

    prefix_mapping = {
        "prefill.nats.auth": "auth",
    }
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    derived_password = "nbs_6f0bc322c483ff43630e2e73e51047748dd693d7"

    @pytest.mark.skip(reason="Chart doesn't use nubus-common password generation")
    def test_auth_password_has_random_value(self, chart):
        pass
