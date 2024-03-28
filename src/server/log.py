# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

from src.server.config import settings


def setup():
    app_logger = logging.getLogger("app")
    app_logger.setLevel(settings.log_level)
    logging.captureWarnings(True)
