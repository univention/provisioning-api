# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

from asgi_correlation_id import CorrelationIdFilter

from server.config import settings

FILE_LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(correlation_id)s] [%(module)s.%(funcName)s:%(lineno)d] %(message)s"


def setup_logging() -> None:
    logging.captureWarnings(True)
    formatter = logging.Formatter(fmt=FILE_LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setLevel(settings.log_level)
    handler.setFormatter(formatter)
    cid_filter = CorrelationIdFilter(uuid_length=10)
    handler.addFilter(cid_filter)
    logger = logging.getLogger()
    logger.setLevel(settings.log_level)
    logger.addHandler(handler)
    for name in ("uvicorn.access", "uvicorn.error"):  # replace the already existing handlers for uvicorn with ours
        logger = logging.getLogger(name)
        logger.handlers = [handler]
