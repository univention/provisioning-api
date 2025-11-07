# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.best_practice.labels import Labels


class TestLabels(Labels):

    def adjust_values(self, values: dict):

        values.setdefault("natsBox", {})["enabled"] = True
        values.setdefault("reloader", {})["enabled"] = True

        return values
