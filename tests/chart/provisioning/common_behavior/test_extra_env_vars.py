# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.best_practice.extra_env_vars import ExtraEnvVars
from univention.testing.helm.utils import apply_mapping


class TestExtraEnvVars(ExtraEnvVars):
    def adjust_values(self, values: dict):
        mapping = {
            "api.extraEnvVars": "extraEnvVars",
            "dispatcher.extraEnvVars": "extraEnvVars",
            "udmTransformer.extraEnvVars": "extraEnvVars",
            "prefill.extraEnvVars": "extraEnvVars",
            "registerConsumers.extraEnvVars": "extraEnvVars",
        }
        apply_mapping(values, mapping, copy=True)
        values.pop("extraEnvVars", {})
        return values
