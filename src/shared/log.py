import logging

from shared.config import settings


def setup():
    app_logger = logging.getLogger("app")
    app_logger.setLevel(settings.log_level)
    logging.captureWarnings(True)
