# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
import uuid

from asgi_correlation_id import correlation_id

from univention.provisioning.utils.log import setup_logging


def test_setup_logging(capsys):
    """Test log format is correct and includes the request ID."""
    req_id = uuid.uuid4().hex[:10]
    correlation_id.set(req_id)
    setup_logging(logging.INFO)
    logger = logging.getLogger("foo")
    logger.info("bar")
    captured = capsys.readouterr()
    assert "bar" in captured.err
    assert "[test_log.test_setup_logging:" in captured.err
    assert f"[{req_id}]" in captured.err
