# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import logging

import aiohttp
from tenacity import after_log, before_sleep_log, retry_if_exception_type, stop_after_attempt, wait_exponential
from tenacity import retry as retry_tenacity


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
                retry=retry_if_exception_type(aiohttp.ClientResponseError | aiohttp.ClientConnectionError),
            )(function)(self, *args, **kwargs)

        return wrapper

    return decorator
