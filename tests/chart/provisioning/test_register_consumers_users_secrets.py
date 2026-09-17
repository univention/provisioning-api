# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from pathlib import Path

import pytest
from pytest_helm.helm import Helm
from pytest_helm.utils import load_yaml

from univention.testing.helm.auth_flavors.password_usage import AuthPasswordUsageViaProjectedVolume
from univention.testing.helm.client.base import BaseTest


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


class TestRegisterConsumersJobWithoutConsumers(BaseTest):
    def test_job_is_not_rendered_when_no_consumers_are_configured(self, chart_path, request):
        # linter_values.yaml sets registerConsumers.createUsers.portal-consumer as a
        # stub. Helm deep-merges values files, so an override can't reliably clear
        # that key: whether a null-valued key is dropped from the merged map differs
        # between Helm versions. Instead, take linter_values.yaml as-is and remove
        # the stub in Python, so createUsers is genuinely absent/empty.
        values = load_yaml(Path(chart_path, "linter_values.yaml").read_text())
        del values["registerConsumers"]["createUsers"]

        helm = Helm(request.config.option.helm_path, [], request.config.option.helm_debug)
        result = helm.helm_template(chart_path, values, "templates/job-register-consumer.yaml")

        with pytest.raises(LookupError):
            result.get_resource(kind="Job", name="release-name-provisioning-register-consumers-1")
