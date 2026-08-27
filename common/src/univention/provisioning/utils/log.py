# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(correlation_id)s] [%(module)s.%(funcName)s:%(lineno)d] %(message)s"


class NoCorrelationIdFilter(logging.Filter):
    """Populates the correlation_id field LOG_FORMAT needs, for services without an ASGI app."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = None
        return True


def setup_logging(log_level: str, correlation_id_filter: logging.Filter | None = None) -> None:
    """Configure the root logger.

    ASGI services pass asgi_correlation_id.CorrelationIdFilter so their log lines
    carry the request ID. Everything else gets NoCorrelationIdFilter and logs
    "None" in that position.
    """
    logging.captureWarnings(True)
    formatter = logging.Formatter(fmt=LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(formatter)
    handler.addFilter(correlation_id_filter or NoCorrelationIdFilter())
    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(handler)
    for name in ("uvicorn.access", "uvicorn.error"):  # replace the already existing handlers for uvicorn with ours
        logger = logging.getLogger(name)
        logger.handlers = [handler]
