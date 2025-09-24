# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.auth_flavors.nats import NatsCreateUserMixin
from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaEnv
from univention.testing.helm.auth_flavors.secret_generation import AuthSecretGenerationOwner
from univention.testing.helm.auth_flavors.username import AuthUsername, AuthUsernameViaEnv


class Config:
    workload_name = "release-name-provisioning-api"
    secret_name = "release-name-provisioning-api-nats"

    prefix_mapping = {
        "api.nats.auth": "auth",
    }
    sub_path_env_password = "env[?@name=='NATS_PASSWORD']"
    derived_password = "4c6cb2fa7b87ec087e08518950ba6451fd6f7184"
    default_username = "api"


class TestAuth(Config, AuthSecretGenerationOwner, AuthPasswordUsageViaEnv): ...


class TestAuthUsername(Config, AuthUsernameViaEnv):
    sub_path_env_username = "env[?@name=='NATS_USER']"


class TestAuthNats(NatsCreateUserMixin, Config, AuthPasswordUsageViaEnv, AuthUsername):
    prefix_mapping = {"nats.config.createUsers.provisioningApi.auth": "auth"}
    env_password = "PROVISIONINGAPI"
    sub_path_env_password = "env[?@name=='PROVISIONINGAPI']"


class TestWaitForNatsAuthPassword(Config, AuthPasswordUsageViaEnv):
    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-nats']"
