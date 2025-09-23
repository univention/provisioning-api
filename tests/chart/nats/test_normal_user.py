# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import subprocess
import pytest
from univention.testing.helm.client.base import BaseTest
from univention.testing.helm.client.nats import SecretUsageViaEnv


class TestNormalUserNatsConfig(BaseTest, SecretUsageViaEnv):
    secret_default_key = "password"
    workload_kind = "StatefulSet"
    workload_name = "release-name-nats"
    config_map_name = "release-name-nats-config"

    prefix_mapping = {"config.createUsers.normalUser.auth": "auth"}
    env_password = "NORMALUSER"
    sub_path_env_password = "env[?@name=='NORMALUSER']"

    def test_user_in_nats_conf(self, chart):
        values = self.load_and_map(
            """
            auth:
              username: "normal-user"
              existingSecret:
                name: "stub-secret-name"
            """)
        result = chart.helm_template(values)
        config_map = result.get_resource(kind="ConfigMap", name=self.config_map_name)
        config = config_map["data"]["nats.conf"]
        assert f"password: ${self.env_password}" in config

    def test_auth_existing_secret_uses_password(self, chart):
        values = self.load_and_map(
            """
            auth:
              username: "normal-user"
              existingSecret:
                name: "stub-secret-name"
            """)
        result = chart.helm_template(values)
        self.assert_correct_secret_usage(result, name="stub-secret-name")

    def test_auth_existing_secret_uses_correct_default_key(self, chart):
        values = self.load_and_map(
            """
            auth:
              username: "normal-user"
              existingSecret:
                name: "stub-secret-name"
            """)
        result = chart.helm_template(values)
        self.assert_correct_secret_usage(result, key=self.secret_default_key)

    def test_auth_existing_secret_uses_correct_custom_key(self, chart):
        values = self.load_and_map(
            """
            auth:
              username: "normal-user"
              existingSecret:
                name: "stub-secret-name"
                keyMapping:
                  password: "stub_password_key"
            """)
        result = chart.helm_template(values)
        self.assert_correct_secret_usage(result, key="stub_password_key")

    def test_auth_existing_secret_is_required(self, chart):
        values = self.load_and_map(
            """
            auth:
              username: "normal-user"
              existingSecret: null
            """)
        with pytest.raises(subprocess.CalledProcessError) as error:
            chart.helm_template(values)
        assert "auth.existingSecret.name is required" in error.value.stderr

    def test_auth_username_is_required(self, chart):
        values = self.load_and_map(
            """
            auth:
              existingSecret:
                  name: "stub-secret-name"
            """)
        with pytest.raises(subprocess.CalledProcessError) as error:
            chart.helm_template(values)
        assert "auth.username is required" in error.value.stderr
