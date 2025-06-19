# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.provisioning_api import RegistrationSecretUsage, SecretViaProjectedVolume


class TestAuth(SecretViaProjectedVolume, RegistrationSecretUsage):
    workload_kind = "Job"
    workload_name = "release-name-provisioning-register-consumers-1"
