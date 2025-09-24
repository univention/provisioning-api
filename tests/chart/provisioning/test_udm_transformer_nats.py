# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.nats import (
    AuthPassword,
    SecretUsageViaEnv,
)


class TestAuthPassword(SecretUsageViaEnv, AuthPassword):
    is_secret_owner = True
    workload_name = "release-name-provisioning-udm-transformer"
    secret_name = "release-name-provisioning-udm-transformer-nats"

    prefix_mapping = {
        "udmTransformer.nats": "nats",
    }


class TestWaitForNatsAuthPassword(TestAuthPassword):
    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-nats']"
