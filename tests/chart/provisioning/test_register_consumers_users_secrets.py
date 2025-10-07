# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaProjectedVolume


class TestDispatcherApiUsesProvisioningApiNatsSecretByEnv(AuthPasswordUsageViaProjectedVolume):
    secret_name = "stub-secret-name"
    prefix_mapping = {"registerConsumers.createUsers.consumerName": "auth"}

    # for AuthPasswordUsageViaProjectedVolume
    volume_name = "consumer-secrets"
    secret_default_key = "registration"
    workload_name = "release-name-provisioning-register-consumers-1"
    workload_kind = "Job"

    @pytest.mark.skip(reason="Consumer secrets can only be configured as existing secret.")
    def test_auth_disabling_existing_secret_by_setting_it_to_null(self): ...

    @pytest.mark.skip(reason="Won't work because of helm context mismatch.")
    def test_keymapping_is_templated(self): ...
