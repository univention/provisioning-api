# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging
from http import HTTPStatus

import aiohttp
from tenacity import after_log, before_sleep_log, retry_if_exception, stop_after_attempt, wait_exponential
from tenacity import retry as retry_tenacity

NON_RETRYABLE_STATUSES = {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}


def is_retryable(error: BaseException) -> bool:
    if isinstance(error, aiohttp.ClientResponseError):
        return error.status not in NON_RETRYABLE_STATUSES
    return isinstance(error, aiohttp.ClientConnectionError)


def retry(logger):
    def decorator(function):
        def wrapper(self, *args, **kwargs):
            return retry_tenacity(
                after=after_log(logger, logging.INFO),
                before_sleep=before_sleep_log(logger, logging.INFO),
                wait=wait_exponential(
                    multiplier=1,
                    min=self.settings.network_retry_starting_interval,
                    max=self.settings.network_retry_max_delay,
                ),
                stop=stop_after_attempt(self.settings.network_retry_max_attempts),
                retry=retry_if_exception(is_retryable),
            )(function)(self, *args, **kwargs)

        return wrapper

    return decorator
