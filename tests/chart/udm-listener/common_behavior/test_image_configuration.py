# SPDX-FileCopyrightText: 2024-2025 Univention GmbH
# SPDX-License-Identifier: AGPL-3.0-only

from univention.testing.helm.best_practice.image_configuration import ImageConfiguration
from univention.testing.helm.utils import apply_mapping


class TestImageConfiguration(ImageConfiguration):
    def adjust_values(self, values: dict):
        mapping = {
            "waitForDependency.image": "image",
        }
        apply_mapping(values, mapping, copy=True)

        return values
