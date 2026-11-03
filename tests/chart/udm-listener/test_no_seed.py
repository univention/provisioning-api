# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from contextlib import nullcontext as does_not_raise

import pytest
from pytest_helm.utils import load_yaml


@pytest.mark.parametrize("generate_passwords", ["true", "false"])
def test_renders_without_a_seed_when_every_password_is_set(chart, generate_passwords):
    """
    The NATS secrets must not read the seed when a password is set.
    A null seed used to crash the derivation even though its result was discarded.
    """
    values = load_yaml(
        f"""
        global:
          secrets:
            generatePasswords: {generate_passwords}
            masterPassword: null
        """
    )
    with does_not_raise():
        chart.helm_template(values)
