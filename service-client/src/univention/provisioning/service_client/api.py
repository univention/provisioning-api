# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""Synchronous, secret-safe access to the Provisioning REST API."""

from __future__ import annotations

import math
import time
from collections.abc import Callable, Mapping
from typing import Any
from urllib.parse import quote, urlsplit, urlunsplit

import requests

DEFAULT_CONNECT_TIMEOUT = 2.0
DEFAULT_READ_TIMEOUT = 5.0
DEFAULT_TIMEOUT = (DEFAULT_CONNECT_TIMEOUT, DEFAULT_READ_TIMEOUT)
# Eleven quick failures with ten three-second delays observe a full 30-second
# App Center dependency startup window. Attempts and retry sleeps are capped,
# and every attempt has separate finite connection and read inactivity limits.
DEFAULT_MAX_ATTEMPTS = 11
DEFAULT_RETRY_DELAY = 3.0

RequestTimeout = float | tuple[float, float]


class APIError(RuntimeError):
    """Base class for failures while using the Provisioning API."""

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class APIConnectionError(APIError):
    """The Provisioning API could not be reached securely."""

    def __init__(self) -> None:
        super().__init__("Could not connect to the Provisioning API.")


class APIAuthenticationError(APIError):
    """The supplied Basic Authentication credentials were rejected."""

    def __init__(self) -> None:
        super().__init__("Provisioning API authentication failed.", status_code=401)


class APINotFoundError(APIError):
    """The requested subscription does not exist."""

    def __init__(self) -> None:
        super().__init__("The Provisioning subscription was not found.", status_code=404)


class APIConflictError(APIError):
    """A subscription with different parameters already exists."""

    def __init__(self) -> None:
        super().__init__(
            "The Provisioning subscription already exists with different parameters.",
            status_code=409,
        )


class APIUnavailableError(APIError):
    """The Provisioning API endpoint exists but is currently unavailable."""

    def __init__(self) -> None:
        super().__init__("The Provisioning API is unavailable.", status_code=503)


class APIResponseError(APIError):
    """The Provisioning API returned an unexpected or malformed response."""

    def __init__(self, *, status_code: int | None = None) -> None:
        if status_code is None:
            message = "The Provisioning API returned an invalid response."
        else:
            message = f"The Provisioning API returned an unexpected HTTP status ({status_code})."
        super().__init__(message, status_code=status_code)


def _normalize_base_url(base_url: str) -> str:
    if not isinstance(base_url, str):
        raise TypeError("Provisioning API base URL must be a string.")

    value = base_url.strip()
    try:
        parsed = urlsplit(value)
        # Accessing port also validates malformed and out-of-range values.
        _ = parsed.port
    except ValueError:
        raise ValueError("Provisioning API base URL is invalid.") from None

    if parsed.scheme.lower() != "https" or not parsed.hostname:
        raise ValueError("Provisioning API base URL must be an absolute HTTPS URL.")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("Provisioning API base URL must not contain credentials.")
    if parsed.query or parsed.fragment:
        raise ValueError("Provisioning API base URL must not contain a query or fragment.")

    path = parsed.path.rstrip("/")
    return urlunsplit(("https", parsed.netloc, path, "", ""))


def _normalize_timeout(timeout: RequestTimeout) -> RequestTimeout:
    def component(value: object) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("Provisioning API timeouts must be finite numbers greater than zero.")
        normalized = float(value)
        if normalized <= 0 or not math.isfinite(normalized):
            raise ValueError("Provisioning API timeouts must be finite numbers greater than zero.")
        return normalized

    if isinstance(timeout, tuple):
        if len(timeout) != 2:
            raise ValueError("Provisioning API timeout must contain connect and read values.")
        return component(timeout[0]), component(timeout[1])
    return component(timeout)


class ProvisioningAPI:
    """Small wrapper around the subscription endpoints of the Provisioning API."""

    def __init__(
        self,
        base_url: str,
        *,
        session: requests.Session | None = None,
        timeout: RequestTimeout = DEFAULT_TIMEOUT,
        verify: bool | str = True,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
        retry_delay: float = DEFAULT_RETRY_DELAY,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if type(max_attempts) is not int or max_attempts < 1:
            raise ValueError("Provisioning API max_attempts must be a positive integer.")
        if isinstance(retry_delay, bool) or not isinstance(retry_delay, (int, float)):
            raise ValueError("Provisioning API retry_delay must not be negative and must be finite.")
        if retry_delay < 0 or not math.isfinite(retry_delay):
            raise ValueError("Provisioning API retry_delay must not be negative and must be finite.")
        self.base_url = _normalize_base_url(base_url)
        self.subscriptions_url = f"{self.base_url}/v1/subscriptions"
        self.timeout = _normalize_timeout(timeout)
        self.verify = verify
        self.max_attempts = max_attempts
        self.retry_delay = float(retry_delay)
        self._sleep = sleep
        self._session = session if session is not None else requests.Session()

    def _subscription_url(self, name: str) -> str:
        if not isinstance(name, str) or not name:
            raise ValueError("Subscription name must be a non-empty string.")
        return f"{self.subscriptions_url}/{quote(name, safe='')}"

    def _request(
        self,
        method: str,
        url: str,
        *,
        auth: tuple[str, str],
        json: Mapping[str, Any] | None = None,
        retry_transient: bool = False,
    ) -> requests.Response:
        request_kwargs: dict[str, Any] = {
            "allow_redirects": False,
            "auth": auth,
            "timeout": self.timeout,
            "verify": self.verify,
        }
        if json is not None:
            request_kwargs["json"] = dict(json)

        attempts = self.max_attempts if retry_transient else 1
        for attempt in range(1, attempts + 1):
            try:
                response = self._session.request(method, url, **request_kwargs)
            except (requests.ConnectionError, requests.Timeout):
                # Do not expose the exception: it may contain request details.
                if attempt == attempts:
                    raise APIConnectionError() from None
            except requests.RequestException:
                # Other request failures are not known to be transient.
                raise APIConnectionError() from None
            else:
                if response.status_code != 503 or attempt == attempts:
                    return response
                response.close()
            self._sleep(self.retry_delay)

        raise AssertionError("request retry loop ended unexpectedly")

    @staticmethod
    def _raise_for_status(response: requests.Response, expected: set[int]) -> None:
        if response.status_code in expected:
            return
        error_types: dict[int, type[APIError]] = {
            401: APIAuthenticationError,
            404: APINotFoundError,
            409: APIConflictError,
            503: APIUnavailableError,
        }
        error_type = error_types.get(response.status_code)
        if error_type is not None:
            raise error_type()
        raise APIResponseError(status_code=response.status_code)

    @staticmethod
    def _response_object(response: requests.Response) -> dict[str, Any]:
        try:
            value = response.json()
        except (TypeError, ValueError):
            raise APIResponseError() from None
        if not isinstance(value, dict):
            raise APIResponseError()
        return value

    @staticmethod
    def _response_list(response: requests.Response) -> list[dict[str, Any]]:
        try:
            value = response.json()
        except (TypeError, ValueError):
            raise APIResponseError() from None
        if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
            raise APIResponseError()
        return value

    def get_subscription(self, name: str, password: str) -> dict[str, Any]:
        """Return one subscription using its own credentials."""

        response = self._request(
            "GET",
            self._subscription_url(name),
            auth=(name, password),
            retry_transient=True,
        )
        self._raise_for_status(response, {200})
        return self._response_object(response)

    def list_subscriptions(self, admin_username: str, admin_password: str) -> list[dict[str, Any]]:
        """Return every subscription using Provisioning administrator credentials."""

        response = self._request(
            "GET",
            self.subscriptions_url,
            auth=(admin_username, admin_password),
            retry_transient=True,
        )
        self._raise_for_status(response, {200})
        return self._response_list(response)

    def create_subscription(
        self,
        definition: Mapping[str, Any] | object,
        password: str,
        admin_username: str,
        admin_password: str,
    ) -> bool:
        """Create a subscription.

        Return ``True`` for a newly created subscription (HTTP 201) and
        ``False`` when the API confirms that an identical subscription already
        exists (HTTP 200).
        """

        to_api_payload = getattr(definition, "to_api_payload", None)
        to_dict = getattr(definition, "to_dict", None)
        if callable(to_api_payload):
            source = to_api_payload(password)
        elif callable(to_dict):
            source = to_dict()
        else:
            source = definition
        if not isinstance(source, Mapping):
            raise TypeError("Subscription definition must be a mapping.")
        try:
            payload = {
                "name": source["name"],
                "realms_topics": source["realms_topics"],
                "request_prefill": source["request_prefill"],
                # Always use the explicit password argument. This prevents a
                # stale or untrusted password in imported JSON from winning.
                "password": password,
            }
        except KeyError as exc:
            raise ValueError("Subscription definition is missing a required field.") from exc

        response = self._request(
            "POST",
            self.subscriptions_url,
            auth=(admin_username, admin_password),
            json=payload,
            retry_transient=True,
        )
        self._raise_for_status(response, {200, 201})
        return response.status_code == 201

    def delete_subscription(self, name: str, password: str) -> None:
        """Delete exactly one subscription using its own credentials."""

        response = self._request("DELETE", self._subscription_url(name), auth=(name, password))
        self._raise_for_status(response, {200})

    def admin_delete_subscription(self, name: str, admin_username: str, admin_password: str) -> None:
        """Delete exactly one subscription using administrator credentials."""

        response = self._request(
            "DELETE",
            self._subscription_url(name),
            auth=(admin_username, admin_password),
        )
        self._raise_for_status(response, {200})
