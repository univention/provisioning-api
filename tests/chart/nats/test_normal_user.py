# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.nats import NatsCreateUserMixin


class TestNormalUserPassword(NatsCreateUserMixin, AuthPasswordUsageViaEnv):
    workload_name = "release-name-nats"
    config_map_name = "release-name-nats-config"
    secret_name = "release-name-nats-admin"

    prefix_mapping = {"config.createUsers.normalUser.auth": "auth"}

    env_password = "NORMALUSER"
    sub_path_env_password = "env[?@name=='NORMALUSER']"

    def adjust_values(self, values: dict):
        values["config"]["createUsers"]["normalUser"]["auth"]["username"] = "normal-username"
        values["config"]["createUsers"]["normalUser"].setdefault("permissions", {})
        return values
