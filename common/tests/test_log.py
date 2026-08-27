# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

from univention.provisioning.utils.log import setup_logging


def test_setup_logging(capsys):
    """Test log format is correct."""
    setup_logging(logging.INFO)
    logger = logging.getLogger("foo")
    logger.info("bar")
    captured = capsys.readouterr()
    assert "bar" in captured.err
    assert "[test_log.test_setup_logging:" in captured.err


def test_setup_logging_without_a_correlation_id(capsys):
    """Services without an ASGI app still have to satisfy the correlation_id field."""
    setup_logging(logging.INFO)
    logging.getLogger("foo").info("bar")
    assert "[None]" in capsys.readouterr().err


def test_setup_logging_honours_a_custom_correlation_id_filter(capsys):
    class StubFilter(logging.Filter):
        def filter(self, record):
            record.correlation_id = "deadbeef42"
            return True

    setup_logging(logging.INFO, StubFilter())
    logging.getLogger("foo").info("bar")
    assert "[deadbeef42]" in capsys.readouterr().err
