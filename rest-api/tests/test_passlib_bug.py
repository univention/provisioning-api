# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging

import pytest
from passlib.context import CryptContext


@pytest.mark.xfail()
def test_passlib_logs_traceback(caplog):
    """Flaky but useful for documentation and demonstration purposes"""
    with caplog.at_level(logging.DEBUG):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        pwd_context.hash("test")

    assert "Traceback" in caplog.text
    assert "in _load_backend_mixin\n    version = _bcrypt.__about__.__version__" in caplog.text


def test_passlib_logs_no_traceback(caplog):
    with caplog.at_level(logging.DEBUG):
        # Execute workaround

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        pwd_context.hash("test")

    assert "Traceback" not in caplog.text
