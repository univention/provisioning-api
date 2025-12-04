# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.best_practice.extra_env_vars import ExtraEnvVars


class TestExtraEnvVars(ExtraEnvVars):
    def adjust_values(self, values: dict):
        pass
