# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.best_practice.image_configuration import (
    ImageConfiguration,
)
from univention.testing.helm.utils import apply_mapping


class TestImageConfiguration(ImageConfiguration):

    def adjust_values(self, values: dict):
        mapping = {
            "nats.image": "image",
            "reloader.image": "image",
            "natsBox.image": "image",
        }
        values.setdefault("natsBox", {})["enabled"] = True
        values.setdefault("reloader", {})["enabled"] = True

        apply_mapping(values, mapping, copy=True)

        return values
