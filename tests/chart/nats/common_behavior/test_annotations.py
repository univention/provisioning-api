# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.best_practice.annotations import Annotations


class TestAnnotations(Annotations):
    def adjust_values(self, values: dict):

        values.setdefault("natsBox", {})["enabled"] = True
        values.setdefault("reloader", {})["enabled"] = True

        return values

    pass
