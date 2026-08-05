# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import Mock, call

import pytest
import requests

from univention.provisioning.service_client.api import (
    DEFAULT_MAX_ATTEMPTS,
    DEFAULT_RETRY_DELAY,
    DEFAULT_TIMEOUT,
    APIAuthenticationError,
    APIConflictError,
    APIConnectionError,
    APINotFoundError,
    APIResponseError,
    APIUnavailableError,
    ProvisioningAPI,
)

BASE_URL = "https://primary.example.test/univention/provisioning"
SUBSCRIPTION = {
    "name": "ox-connector-member",
    "realms_topics": [{"realm": "udm", "topic": "users/user"}],
    "request_prefill": True,
}
SUBSCRIPTION_STATUS = {**SUBSCRIPTION, "prefill_queue_status": "done"}


def response(status_code: int, data: object | None = None, *, body: str = "") -> Mock:
    result = Mock(spec=requests.Response)
    result.status_code = status_code
    result.text = body
    if data is not None:
        result.json.return_value = data
    return result


def client(result: Mock, **kwargs: object) -> tuple[ProvisioningAPI, Mock]:
    session = Mock(spec=requests.Session)
    session.request.return_value = result
    kwargs.setdefault("sleep", Mock())
    return ProvisioningAPI(BASE_URL, session=session, **kwargs), session


@pytest.mark.parametrize(
    ("value", "normalized"),
    [
        (f"  {BASE_URL}/  ", BASE_URL),
        ("HTTPS://PRIMARY.EXAMPLE.TEST/", "https://PRIMARY.EXAMPLE.TEST"),
        ("https://[2001:db8::1]:8443/api/", "https://[2001:db8::1]:8443/api"),
    ],
)
def test_normalizes_https_base_url(value: str, normalized: str) -> None:
    api = ProvisioningAPI(value)

    assert api.base_url == normalized
    assert api.subscriptions_url == f"{normalized}/v1/subscriptions"


@pytest.mark.parametrize(
    "value",
    [
        "",
        "primary.example.test/api",
        "http://primary.example.test/api",
        "https:///api",
        "https://user:password@primary.example.test/api",
        "https://primary.example.test/api?secret=value",
        "https://primary.example.test/api#fragment",
        "https://primary.example.test:99999/api",
    ],
)
def test_rejects_unsafe_or_invalid_base_url(value: str) -> None:
    with pytest.raises(ValueError):
        ProvisioningAPI(value)


def test_rejects_non_string_base_url() -> None:
    with pytest.raises(TypeError):
        ProvisioningAPI(None)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "timeout",
    [0, -1, float("inf"), float("nan"), (1, 0), (1, float("inf")), (1,), True, "10"],
)
def test_rejects_invalid_timeout(timeout: object) -> None:
    with pytest.raises(ValueError, match="Provisioning API timeout"):
        ProvisioningAPI(BASE_URL, timeout=timeout)  # type: ignore[arg-type]


@pytest.mark.parametrize("max_attempts", [0, -1, 1.5, True])
def test_rejects_invalid_max_attempts(max_attempts: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        ProvisioningAPI(BASE_URL, max_attempts=max_attempts)  # type: ignore[arg-type]


@pytest.mark.parametrize("retry_delay", [-0.1, float("inf"), float("nan"), True, "1"])
def test_rejects_invalid_retry_delay(retry_delay: object) -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        ProvisioningAPI(BASE_URL, retry_delay=retry_delay)  # type: ignore[arg-type]


def test_default_retry_policy_observes_thirty_second_readiness_window() -> None:
    session = Mock(spec=requests.Session)
    session.request.side_effect = [requests.ConnectionError("secret transport detail")] * DEFAULT_MAX_ATTEMPTS
    sleep = Mock()
    api = ProvisioningAPI(BASE_URL, session=session, sleep=sleep)

    with pytest.raises(APIConnectionError):
        api.get_subscription("ox-member", "subscriber-secret")

    assert session.request.call_count == DEFAULT_MAX_ATTEMPTS == 11
    assert sleep.call_args_list == [call(DEFAULT_RETRY_DELAY)] * (DEFAULT_MAX_ATTEMPTS - 1)
    assert sum(item.args[0] for item in sleep.call_args_list) == 30.0
    assert session.request.call_args.kwargs["timeout"] == DEFAULT_TIMEOUT == (2.0, 5.0)


def test_get_retries_connection_error_and_unavailable_response_until_success() -> None:
    session = Mock(spec=requests.Session)
    unavailable = response(503, body="subscriber-secret in response")
    session.request.side_effect = [
        requests.ConnectionError("subscriber-secret in connection details"),
        unavailable,
        response(200, SUBSCRIPTION_STATUS),
    ]
    sleep = Mock()
    api = ProvisioningAPI(
        BASE_URL,
        session=session,
        max_attempts=3,
        retry_delay=0.25,
        sleep=sleep,
    )

    assert api.get_subscription("ox-member", "subscriber-secret") == SUBSCRIPTION_STATUS
    assert session.request.call_count == 3
    assert sleep.call_args_list == [call(0.25), call(0.25)]
    unavailable.close.assert_called_once_with()


def test_get_does_not_retry_non_transient_request_failure() -> None:
    session = Mock(spec=requests.Session)
    session.request.side_effect = requests.exceptions.InvalidURL("subscriber-secret in URL details")
    sleep = Mock()
    api = ProvisioningAPI(BASE_URL, session=session, max_attempts=3, sleep=sleep)

    with pytest.raises(APIConnectionError) as exc_info:
        api.get_subscription("ox-member", "subscriber-secret")

    session.request.assert_called_once()
    sleep.assert_not_called()
    assert "subscriber-secret" not in str(exc_info.value)
    assert exc_info.value.__cause__ is None


@pytest.mark.parametrize(
    "transient_failure",
    [
        requests.Timeout("admin-secret in timeout details"),
        response(503, body="admin-secret in response"),
    ],
)
def test_idempotent_create_retries_transient_failure(transient_failure: object) -> None:
    session = Mock(spec=requests.Session)
    session.request.side_effect = [transient_failure, response(201)]
    sleep = Mock()
    api = ProvisioningAPI(
        BASE_URL,
        session=session,
        max_attempts=2,
        retry_delay=0.5,
        sleep=sleep,
    )

    assert api.create_subscription(SUBSCRIPTION, "subscriber-secret", "admin", "admin-secret") is True
    assert session.request.call_count == 2
    assert session.request.call_args_list[0] == session.request.call_args_list[1]
    sleep.assert_called_once_with(0.5)


@pytest.mark.parametrize(
    ("failure", "error_type"),
    [
        (requests.ConnectionError("subscriber-secret"), APIConnectionError),
        (response(503, body="subscriber-secret"), APIUnavailableError),
    ],
)
def test_retry_attempts_are_bounded_and_errors_remain_secret_safe(
    failure: object,
    error_type: type[Exception],
) -> None:
    session = Mock(spec=requests.Session)
    session.request.side_effect = [failure, failure, failure]
    sleep = Mock()
    api = ProvisioningAPI(BASE_URL, session=session, max_attempts=3, retry_delay=0.1, sleep=sleep)

    with pytest.raises(error_type) as exc_info:
        api.get_subscription("ox-member", "subscriber-secret")

    assert session.request.call_count == 3
    assert sleep.call_args_list == [call(0.1), call(0.1)]
    assert "subscriber-secret" not in str(exc_info.value)
    assert exc_info.value.__cause__ is None


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (401, APIAuthenticationError),
        (404, APINotFoundError),
        (409, APIConflictError),
        (418, APIResponseError),
        (500, APIResponseError),
    ],
)
def test_get_does_not_retry_non_transient_http_status(status: int, error_type: type[Exception]) -> None:
    session = Mock(spec=requests.Session)
    session.request.return_value = response(status)
    sleep = Mock()
    api = ProvisioningAPI(BASE_URL, session=session, max_attempts=3, sleep=sleep)

    with pytest.raises(error_type):
        api.get_subscription("ox-member", "subscriber-secret")

    session.request.assert_called_once()
    sleep.assert_not_called()


def test_get_subscription_uses_subscriber_credentials_and_encodes_name() -> None:
    api, session = client(response(200, SUBSCRIPTION_STATUS))

    result = api.get_subscription("ox connector/member", "subscriber-secret")

    assert result == SUBSCRIPTION_STATUS
    session.request.assert_called_once_with(
        "GET",
        f"{BASE_URL}/v1/subscriptions/ox%20connector%2Fmember",
        allow_redirects=False,
        auth=("ox connector/member", "subscriber-secret"),
        timeout=DEFAULT_TIMEOUT,
        verify=True,
    )


@pytest.mark.parametrize("timeout", [2.5, (1.25, 4.0)])
def test_get_subscription_propagates_custom_transport_options(timeout: object) -> None:
    api, session = client(
        response(200, SUBSCRIPTION_STATUS),
        timeout=timeout,
        verify="/tmp/test-ca.pem",
    )

    api.get_subscription(SUBSCRIPTION["name"], "subscriber-secret")

    _, call_kwargs = session.request.call_args
    assert call_kwargs["timeout"] == timeout
    assert call_kwargs["verify"] == "/tmp/test-ca.pem"
    assert call_kwargs["allow_redirects"] is False


def test_get_subscription_rejects_empty_name_without_request() -> None:
    api, session = client(response(200, SUBSCRIPTION_STATUS))

    with pytest.raises(ValueError, match="non-empty"):
        api.get_subscription("", "subscriber-secret")

    session.request.assert_not_called()


def test_list_subscriptions_uses_admin_credentials() -> None:
    api, session = client(response(200, [SUBSCRIPTION_STATUS]))

    result = api.list_subscriptions("admin", "admin-secret")

    assert result == [SUBSCRIPTION_STATUS]
    session.request.assert_called_once_with(
        "GET",
        f"{BASE_URL}/v1/subscriptions",
        allow_redirects=False,
        auth=("admin", "admin-secret"),
        timeout=DEFAULT_TIMEOUT,
        verify=True,
    )


@pytest.mark.parametrize(("status", "created"), [(200, False), (201, True)])
def test_create_subscription_sends_exact_full_payload(status: int, created: bool) -> None:
    api, session = client(response(status))
    definition_with_ignored_fields = {
        **SUBSCRIPTION,
        "password": "untrusted-secret",
        "password_file": "/tmp/untrusted",
        "local_state": "candidate",
    }

    result = api.create_subscription(definition_with_ignored_fields, "generated-secret", "admin", "admin-secret")

    assert result is created
    session.request.assert_called_once_with(
        "POST",
        f"{BASE_URL}/v1/subscriptions",
        allow_redirects=False,
        auth=("admin", "admin-secret"),
        json={**SUBSCRIPTION, "password": "generated-secret"},
        timeout=DEFAULT_TIMEOUT,
        verify=True,
    )


def test_create_subscription_accepts_definition_object_with_api_payload() -> None:
    @dataclass
    class Definition:
        received_password: str | None = None

        def to_api_payload(self, password: str) -> dict[str, object]:
            self.received_password = password
            return SUBSCRIPTION

    definition = Definition()
    api, session = client(response(201))

    assert api.create_subscription(definition, "generated-secret", "admin", "admin-secret") is True
    assert definition.received_password == "generated-secret"
    assert session.request.call_args.kwargs["json"]["password"] == "generated-secret"


def test_create_subscription_accepts_definition_object_with_to_dict() -> None:
    @dataclass
    class Definition:
        def to_dict(self) -> dict[str, object]:
            return SUBSCRIPTION

    api, session = client(response(201))

    assert api.create_subscription(Definition(), "generated-secret", "admin", "admin-secret") is True
    assert session.request.call_args.kwargs["json"] == {**SUBSCRIPTION, "password": "generated-secret"}


@pytest.mark.parametrize(
    "definition",
    [
        object(),
        {"name": "incomplete"},
    ],
)
def test_create_subscription_rejects_invalid_definition_without_request(definition: object) -> None:
    api, session = client(response(201))

    with pytest.raises((TypeError, ValueError)):
        api.create_subscription(definition, "generated-secret", "admin", "admin-secret")

    session.request.assert_not_called()


def test_delete_subscription_uses_subscriber_credentials() -> None:
    api, session = client(response(200))

    assert api.delete_subscription("ox/member", "subscriber-secret") is None
    session.request.assert_called_once_with(
        "DELETE",
        f"{BASE_URL}/v1/subscriptions/ox%2Fmember",
        allow_redirects=False,
        auth=("ox/member", "subscriber-secret"),
        timeout=DEFAULT_TIMEOUT,
        verify=True,
    )


def test_admin_delete_subscription_uses_admin_credentials() -> None:
    api, session = client(response(200))

    assert api.admin_delete_subscription("ox-member", "admin", "admin-secret") is None
    session.request.assert_called_once_with(
        "DELETE",
        f"{BASE_URL}/v1/subscriptions/ox-member",
        allow_redirects=False,
        auth=("admin", "admin-secret"),
        timeout=DEFAULT_TIMEOUT,
        verify=True,
    )


@pytest.mark.parametrize("admin", [False, True])
@pytest.mark.parametrize(
    ("failure", "error_type"),
    [
        (requests.ConnectionError("subscriber-secret in connection details"), APIConnectionError),
        (response(503, body="subscriber-secret in response"), APIUnavailableError),
    ],
)
def test_delete_never_retries_transient_failure(
    admin: bool,
    failure: object,
    error_type: type[Exception],
) -> None:
    session = Mock(spec=requests.Session)
    session.request.side_effect = [failure]
    sleep = Mock()
    api = ProvisioningAPI(BASE_URL, session=session, max_attempts=4, sleep=sleep)

    with pytest.raises(error_type):
        if admin:
            api.admin_delete_subscription("ox-member", "admin", "admin-secret")
        else:
            api.delete_subscription("ox-member", "subscriber-secret")

    session.request.assert_called_once()
    sleep.assert_not_called()


@pytest.mark.parametrize(
    ("status", "error_type"),
    [
        (401, APIAuthenticationError),
        (404, APINotFoundError),
        (409, APIConflictError),
        (503, APIUnavailableError),
        (302, APIResponseError),
        (418, APIResponseError),
        (500, APIResponseError),
    ],
)
def test_maps_http_status_without_exposing_response_body(status: int, error_type: type[Exception]) -> None:
    api, _ = client(response(status, body="subscriber-secret raw server detail"))

    with pytest.raises(error_type) as exc_info:
        api.get_subscription("ox-member", "subscriber-secret")

    error = str(exc_info.value)
    assert "subscriber-secret" not in error
    assert "raw server detail" not in error
    assert exc_info.value.status_code == status


@pytest.mark.parametrize(
    "exception",
    [
        requests.ConnectionError("subscriber-secret in connection details"),
        requests.Timeout("subscriber-secret in timeout details"),
        requests.exceptions.SSLError("subscriber-secret in TLS details"),
    ],
)
def test_maps_transport_failures_without_exposing_exception(exception: Exception) -> None:
    session = Mock(spec=requests.Session)
    session.request.side_effect = exception
    api = ProvisioningAPI(BASE_URL, session=session, sleep=Mock())

    with pytest.raises(APIConnectionError) as exc_info:
        api.get_subscription("ox-member", "subscriber-secret")

    assert "subscriber-secret" not in str(exc_info.value)
    assert exc_info.value.__cause__ is None


@pytest.mark.parametrize("value", [None, [], "invalid", 1])
def test_get_subscription_rejects_non_object_json(value: object) -> None:
    api, _ = client(response(200, value))

    with pytest.raises(APIResponseError, match="invalid response"):
        api.get_subscription("ox-member", "subscriber-secret")


@pytest.mark.parametrize("value", [None, {}, "invalid", ["not-an-object"]])
def test_list_subscriptions_rejects_non_list_of_objects(value: object) -> None:
    api, _ = client(response(200, value))

    with pytest.raises(APIResponseError, match="invalid response"):
        api.list_subscriptions("admin", "admin-secret")


@pytest.mark.parametrize("method", ["get_subscription", "list_subscriptions"])
def test_rejects_invalid_json_without_exposing_parser_details(method: str) -> None:
    result = response(200)
    result.json.side_effect = ValueError("subscriber-secret in response")
    api, _ = client(result)

    with pytest.raises(APIResponseError) as exc_info:
        if method == "get_subscription":
            api.get_subscription("ox-member", "subscriber-secret")
        else:
            api.list_subscriptions("admin", "admin-secret")

    assert "subscriber-secret" not in str(exc_info.value)
    assert exc_info.value.__cause__ is None
