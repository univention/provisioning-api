# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner


class Config:
    workload_name = "release-name-provisioning-dispatcher"
    secret_name = "release-name-provisioning-nats-dispatcher"

    prefix_mapping = {
        "dispatcher.nats.auth": "auth",
    }
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    derived_password = "nbs_3721614ab68388ad4913653eb126c3d3ad4d9163"


class TestAuth(Config, AuthSecretGenerationOwner, AuthPasswordUsageViaEnv):
    @pytest.mark.skip(reason="Chart doesn't use nubus-common password generation")
    def test_auth_password_has_random_value(self, chart):
        pass


class TestWaitForNatsAuthPassword(Config, AuthPasswordUsageViaEnv):
    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-nats']"
