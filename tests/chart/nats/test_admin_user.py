# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import subprocess
import pytest
from univention.testing.helm.client.base import BaseTest
from univention.testing.helm.client.nats import (
    AuthPassword,
    SecretUsageViaEnv,
)


class TestAdminUserNatsConfig(SecretUsageViaEnv, AuthPassword):
    is_secret_owner = True
    workload_kind = "StatefulSet"
    workload_name = "release-name-nats"
    config_map_name = "release-name-nats-config"
    secret_name = "release-name-nats-admin"

    prefix_mapping = {"config.createUsers.adminUser.auth": "nats.auth"}

    env_password = "ADMINUSER"
    sub_path_env_password = "env[?@name=='ADMINUSER']"

    def test_user_in_nats_conf(self, chart):
        result = chart.helm_template()
        config_map = result.get_resource(kind="ConfigMap", name=self.config_map_name)
        config = config_map["data"]["nats.conf"]
        assert f"password: ${self.env_password}" in config


class TestAdminPasswordNatsBox(SecretUsageViaEnv, AuthPassword):
    is_secret_owner = True
    workload_kind = "StatefulSet"

    workload_name = "release-name-nats"
    secret_name = "release-name-nats-admin"

    prefix_mapping = {"config.createUsers.adminUser.auth": "nats.auth"}

    path_container = "..spec.template.spec.containers[?@.name=='nats-box']"
