# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.nats import (
    AuthPassword,
    SecretUsageViaEnv,
)


class TestAuthPassword(SecretUsageViaEnv, AuthPassword):
    workload_name = "release-name-provisioning-dispatcher"
    secret_name = "release-name-provisioning-dispatcher-nats"

    prefix_mapping = {
        "dispatcher.nats": "nats",
    }


class TestWaitForNatsAuthPassword(TestAuthPassword):

    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-nats']"
