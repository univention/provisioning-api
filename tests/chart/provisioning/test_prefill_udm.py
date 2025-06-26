# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.udm import AuthPassword, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPassword):
    config_map_name = "release-name-provisioning-prefill"
    secret_name = "release-name-provisioning-prefill-udm"
    workload_name = "release-name-provisioning-prefill"

    prefix_mapping = {
        "prefill.udm": "udm",
    }


class TestAuthWaitForUdm(TestAuth):
    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-udm']"
