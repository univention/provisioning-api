# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import subprocess

import pytest

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaProjectedVolume


class TestAuth(AuthPasswordUsageViaProjectedVolume):
    """
    Checks the correct secret usage around the user registration.

    This Secret usage check is special because the registration requires an
    existing secret to be configured. Most other implementations support to
    provide also a value in a key like `password` directly.
    """

    workload_kind = "Job"
    workload_name = "release-name-provisioning-register-consumers-1"

    prefix_mapping = {
        "auth.existingSecret.keyMapping.registration": "auth.existingSecret.keyMapping.password",
        "registerConsumers.createUsers.consumerName": "auth",
    }

    secret_name = "stub-secret-name"
    secret_default_key = "registration"
    volume_name = "consumer-secrets"

    @pytest.mark.skip("Existing secret is the only option and can't be set to null")
    def test_auth_disabling_existing_secret_by_setting_it_to_null(self, chart): ...

    def test_auth_existing_secret_is_required(self, chart):
        values = self.load_and_map(
            """
            auth:
              existingSecret: null
            """
        )
        with pytest.raises(subprocess.CalledProcessError) as error:
            chart.helm_template(values)
        assert "Consumer secrets can only be configured as existing secret" in error.value.stderr
