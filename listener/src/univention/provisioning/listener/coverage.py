# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import os

from univention.listener.handler_logging import get_logger

cov = None
logger = get_logger("provisioning_handler")

if os.environ.get("COVERAGE_PROCESS_START"):
    logger.info("Recording coverage. COVERAGE_PROCESS_START=%r", os.environ.get("COVERAGE_PROCESS_START"))
    import coverage

    cov = coverage.Coverage.current()
    if not cov:  # pragma: no cover
        logger.error("Cannot access coverage instance.")


def save_coverage():
    if os.environ.get("COVERAGE_PROCESS_START") and cov:
        try:
            cov.save()
        except Exception as exc:  # pragma: no cover
            logger.warning("Error storing coverage report: %s", str(exc))
            logger.warning("Coverage configuration: %r", cov.config)
