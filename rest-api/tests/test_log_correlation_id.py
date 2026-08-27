# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import logging
import uuid

from asgi_correlation_id import CorrelationIdFilter, correlation_id

from univention.provisioning.utils.log import setup_logging


def test_setup_logging_includes_the_request_id(capsys):
    """Moved here from common/tests: asgi-correlation-id is a rest-api dependency now."""
    req_id = uuid.uuid4().hex[:10]
    correlation_id.set(req_id)
    setup_logging(logging.INFO, CorrelationIdFilter(uuid_length=10))
    logger = logging.getLogger("foo")
    logger.info("bar")
    captured = capsys.readouterr()
    assert "bar" in captured.err
    assert f"[{req_id}]" in captured.err
