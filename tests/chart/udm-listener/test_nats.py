# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.nats import (
    AuthPassword,
    SecretUsageViaEnv,
)


class TestAuthPassword(SecretUsageViaEnv, AuthPassword):
    workload_kind = "StatefulSet"
    workload_name = "release-name-udm-listener"
    secret_name = "release-name-udm-listener-nats"
