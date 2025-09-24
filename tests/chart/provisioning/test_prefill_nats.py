# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.nats import (
    AuthPassword,
    SecretUsageViaEnv,
)


class TestAuthPassword(SecretUsageViaEnv, AuthPassword):
    is_secret_owner = True
    workload_name = "release-name-provisioning-prefill"
    secret_name = "release-name-provisioning-prefill-nats"

    prefix_mapping = {
        "prefill.nats": "nats",
    }
