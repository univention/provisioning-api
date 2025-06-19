# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.udm import AuthPassword, SecretViaEnv


class TestAuth(SecretViaEnv, AuthPassword):
    config_map_name = "release-name-provisioning-register-consumers"
    secret_name = "release-name-provisioning-register-consumers-udm"
    workload_kind = "Job"

    path_container = "spec.template.spec.initContainers[?@.name=='wait-for-data-loader']"

    prefix_mapping = {
        "registerConsumers.udm": "udm",
    }
