# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import base64
import json
import logging
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

from univention.provisioning.consumer import register
from univention.provisioning.consumer.kubernetes_secrets import KubernetesSecretReader
from univention.provisioning.consumer.register import RegisterConsumersSettings, register_all

NAMESPACE = "nubus"
SECRETS_PATH = f"/api/v1/namespaces/{NAMESPACE}/secrets"
ADMIN_PASSWORD = "admin-secret-pw"


def spec(name: str, password="consumer-secret-pw", **overrides) -> dict:
    return {
        "name": name,
        "realms_topics": [{"realm": "udm", "topic": "users/user"}],
        "request_prefill": False,
        "password": password,
    } | overrides


def reference(name: str, key: str = "password") -> dict:
    return {"kubernetesSecret": {"name": name, "key": key}}


@pytest.fixture
def specs_dir(tmp_path: Path) -> Path:
    return tmp_path


def write(specs_dir: Path, **specs):
    for filename, content in specs.items():
        text = content if isinstance(content, str) else json.dumps(content)
        (specs_dir / f"{filename}.json").write_text(text)


@pytest.fixture
def settings(httpserver: HTTPServer, specs_dir: Path) -> RegisterConsumersSettings:
    return RegisterConsumersSettings(
        provisioning_api_base_url=httpserver.url_for("/"),
        admin_username="admin",
        admin_password=ADMIN_PASSWORD,
        specs_dir=specs_dir,
        retry_attempts=3,
        retry_delay=0,
    )


class ProvisioningApi:
    """Answers POST /v1/subscriptions with the statuses queued per subscription name."""

    def __init__(self, httpserver: HTTPServer, statuses: dict[str, list[int] | int]):
        self.statuses = {name: list(s) if isinstance(s, list) else [s] for name, s in statuses.items()}
        self.received: list[dict] = []
        httpserver.expect_request("/v1/subscriptions", method="POST").respond_with_handler(self.handle)

    def handle(self, request: Request) -> Response:
        body = request.get_json()
        self.received.append(body)
        queue = self.statuses[body["name"]]
        status = queue.pop(0) if len(queue) > 1 else queue[0]
        return Response(json.dumps({"detail": f"answer {status}"}), status=status, content_type="application/json")

    def names(self) -> list[str]:
        return [body["name"] for body in self.received]


@pytest.fixture
def k8s_api(httpserver: HTTPServer):
    """The Kubernetes API on the same test server, and a reader factory that counts how often it is built."""
    built = []

    def factory():
        built.append(True)
        return KubernetesSecretReader(httpserver.url_for("/"), NAMESPACE, "sa-token", ssl_context=None)

    def add_secret(name: str, data: dict[str, str]):
        encoded = {key: base64.b64encode(value.encode()).decode() for key, value in data.items()}
        httpserver.expect_request(f"{SECRETS_PATH}/{name}").respond_with_json({"data": encoded})

    factory.built = built
    factory.add_secret = add_secret
    return factory


async def test_string_password_is_posted_unchanged(httpserver, settings, specs_dir, k8s_api):
    write(specs_dir, portal=spec("portal-consumer", password='p@ss: "w0rd" #'))
    api = ProvisioningApi(httpserver, {"portal-consumer": 201})

    assert await register_all(settings, k8s_api) == 0

    assert api.received == [spec("portal-consumer", password='p@ss: "w0rd" #')]
    assert k8s_api.built == [], "the Kubernetes reader is only built for a reference"


async def test_reference_is_resolved_from_the_secret(httpserver, settings, specs_dir, k8s_api):
    write(specs_dir, portal=spec("portal-consumer", password=reference("portal-consumer-pw")))
    k8s_api.add_secret("portal-consumer-pw", {"password": "from-the-secret"})
    api = ProvisioningApi(httpserver, {"portal-consumer": 201})

    assert await register_all(settings, k8s_api) == 0

    assert api.received == [spec("portal-consumer", password="from-the-secret")]


async def test_shared_secret_is_read_once(httpserver, settings, specs_dir, k8s_api):
    write(
        specs_dir,
        a=spec("a", password=reference("shared", "a")),
        b=spec("b", password=reference("shared", "b")),
    )
    k8s_api.add_secret("shared", {"a": "pw-a", "b": "pw-b"})
    api = ProvisioningApi(httpserver, {"a": 201, "b": 201})

    assert await register_all(settings, k8s_api) == 0

    assert [body["password"] for body in api.received] == ["pw-a", "pw-b"]
    assert sum(1 for request, _ in httpserver.log if request.path.startswith(SECRETS_PATH)) == 1
    assert len(k8s_api.built) == 1


@pytest.mark.parametrize(
    "content,message",
    [
        ("{not json", "not valid JSON"),
        ("[]", "must be a JSON object"),
        (spec("x", password=reference("s") | {"default": "y"}), "invalid password reference"),
        (spec("x", password={"name": "s", "key": "k"}), "password must be a string or"),
        (spec("x", password=123), "password must be a string or"),
        ({"name": "x", "password": "pw"}, "invalid spec: realms_topics: Field required"),
        (spec("x", realms_topics="udm"), "invalid spec: realms_topics"),
    ],
)
async def test_invalid_spec_fails_before_the_request(
    httpserver, settings, specs_dir, k8s_api, caplog, content, message
):
    write(specs_dir, broken=content)
    api = ProvisioningApi(httpserver, {})

    assert await register_all(settings, k8s_api) == 1

    assert api.received == []
    assert "Failed to register the consumer broken" in caplog.text
    assert message in caplog.text


@pytest.mark.parametrize(
    "status,message",
    [(201, "Registered the consumer portal"), (200, "already registered with the same parameters")],
)
async def test_success(httpserver, settings, specs_dir, k8s_api, caplog, status, message):
    caplog.set_level(logging.INFO)
    write(specs_dir, portal=spec("portal-consumer"))
    ProvisioningApi(httpserver, {"portal-consumer": status})

    assert await register_all(settings, k8s_api) == 0
    assert message in caplog.text


async def test_conflict_explains_that_changes_are_not_supported(httpserver, settings, specs_dir, k8s_api, caplog):
    write(specs_dir, portal=spec("portal-consumer"))
    api = ProvisioningApi(httpserver, {"portal-consumer": 409})

    assert await register_all(settings, k8s_api) == 1

    assert len(api.received) == 1, "a conflict is not retried"
    assert "already exists with a different password or config" in caplog.text
    assert "deleting the subscription drops its queue" in caplog.text
    assert "answer 409" in caplog.text


async def test_server_error_is_retried(httpserver, settings, specs_dir, k8s_api, caplog):
    write(specs_dir, portal=spec("portal-consumer"))
    api = ProvisioningApi(httpserver, {"portal-consumer": [503, 500, 201]})

    assert await register_all(settings, k8s_api) == 0

    assert len(api.received) == 3
    assert "attempt 1 of 3 failed: HTTP 503" in caplog.text
    assert "attempt 2 of 3 failed: HTTP 500" in caplog.text


async def test_server_error_fails_after_the_last_attempt(httpserver, settings, specs_dir, k8s_api, caplog):
    write(specs_dir, portal=spec("portal-consumer"))
    api = ProvisioningApi(httpserver, {"portal-consumer": 500})

    assert await register_all(settings, k8s_api) == 1

    assert len(api.received) == 3
    assert "HTTP 500. Response: " in caplog.text


@pytest.mark.parametrize("status", [400, 401, 403, 404, 422])
async def test_client_error_is_not_retried(httpserver, settings, specs_dir, k8s_api, status):
    write(specs_dir, portal=spec("portal-consumer"))
    api = ProvisioningApi(httpserver, {"portal-consumer": status})

    assert await register_all(settings, k8s_api) == 1
    assert len(api.received) == 1


async def test_unreachable_api_is_retried_then_fails(settings, specs_dir, k8s_api, caplog, monkeypatch):
    write(specs_dir, portal=spec("portal-consumer"))
    settings.provisioning_api_base_url = "http://127.0.0.1:9"

    assert await register_all(settings, k8s_api) == 1

    assert caplog.text.count("attempt") == 2
    assert "Provisioning API unreachable" in caplog.text


@pytest.mark.parametrize(
    "secret_status,message,attempts",
    [(404, "not found", 1), (403, "denied", 1), (500, "failed with HTTP 500", 3)],
)
async def test_secret_errors_fail_that_spec_only(
    httpserver, settings, specs_dir, k8s_api, caplog, secret_status, message, attempts
):
    write(specs_dir, a=spec("a", password=reference("missing")), b=spec("b"))
    httpserver.expect_request(f"{SECRETS_PATH}/missing").respond_with_data("x", status=secret_status)
    api = ProvisioningApi(httpserver, {"b": 201})

    assert await register_all(settings, k8s_api) == 1

    assert api.names() == ["b"]
    assert message in caplog.text
    assert sum(1 for request, _ in httpserver.log if request.path.endswith("/missing")) == attempts


async def test_missing_key_in_secret(httpserver, settings, specs_dir, k8s_api, caplog):
    write(specs_dir, a=spec("a", password=reference("s", "nope")))
    k8s_api.add_secret("s", {"password": "x"})
    ProvisioningApi(httpserver, {})

    assert await register_all(settings, k8s_api) == 1
    assert "Secret 's' has no key 'nope'" in caplog.text


async def test_without_service_account(httpserver, settings, specs_dir, caplog, tmp_path):
    write(specs_dir, a=spec("a", password=reference("s")))
    ProvisioningApi(httpserver, {})

    def factory():
        return KubernetesSecretReader.from_service_account(tmp_path / "no-sa", {})

    assert await register_all(settings, factory) == 1
    assert "needs the pod's ServiceAccount token" in caplog.text


async def test_every_spec_is_tried_in_order(httpserver, settings, specs_dir, k8s_api):
    write(specs_dir, c=spec("c"), a=spec("a"), b=spec("b"))
    api = ProvisioningApi(httpserver, {"a": 201, "b": 409, "c": 200})

    assert await register_all(settings, k8s_api) == 1
    assert api.names() == ["a", "b", "c"]


async def test_only_json_files_are_specs(httpserver, settings, specs_dir, k8s_api):
    write(specs_dir, a=spec("a"))
    (specs_dir / "a.password").write_text("not a spec")
    api = ProvisioningApi(httpserver, {"a": 201})

    assert await register_all(settings, k8s_api) == 0
    assert api.names() == ["a"]


async def test_no_specs_is_nothing_to_do(settings, k8s_api, caplog):
    caplog.set_level(logging.INFO)

    assert await register_all(settings, k8s_api) == 0
    assert "nothing to register" in caplog.text
    assert k8s_api.built == []


async def test_summary(httpserver, settings, specs_dir, k8s_api, caplog):
    caplog.set_level(logging.INFO)
    write(specs_dir, a=spec("a"), b=spec("b"), c=spec("c"))
    ProvisioningApi(httpserver, {"a": 201, "b": 200, "c": 409})

    await register_all(settings, k8s_api)
    assert "1 created, 1 unchanged, 1 failed" in caplog.text


async def test_log_names_the_reference_but_never_a_password(httpserver, settings, specs_dir, k8s_api, caplog):
    caplog.set_level(logging.DEBUG)
    write(
        specs_dir,
        a=spec("a", password="inline-secret-pw"),
        b=spec("b", password=reference("b-secret")),
        c=spec("c", password="conflicting-secret-pw"),
    )
    k8s_api.add_secret("b-secret", {"password": "resolved-secret-pw"})
    ProvisioningApi(httpserver, {"a": 201, "b": 500, "c": 409})

    await register_all(settings, k8s_api)

    assert "password from Secret 'b-secret' key 'password'" in caplog.text
    assert "password from the spec" in caplog.text
    for secret in ("inline-secret-pw", "resolved-secret-pw", "conflicting-secret-pw", ADMIN_PASSWORD, "sa-token"):
        assert secret not in caplog.text


def test_settings_from_the_job_environment(monkeypatch):
    monkeypatch.setenv("PROVISIONING_API_BASE_URL", "http://provisioning-api")
    monkeypatch.setenv("ADMIN_USERNAME", "admin")
    monkeypatch.setenv("ADMIN_PASSWORD", "pw")
    monkeypatch.delenv("SPECS_DIR", raising=False)

    settings = RegisterConsumersSettings()

    assert settings.specs_dir == Path("/secrets")
    assert settings.retry_attempts == 3
    assert settings.retry_delay == 1.0
    assert "pw" not in repr(settings)


def test_run_exits_with_the_result(monkeypatch, tmp_path):
    monkeypatch.setenv("SPECS_DIR", str(tmp_path))
    write(tmp_path, broken="{not json")

    with pytest.raises(SystemExit) as exit_:
        register.run()
    assert exit_.value.code == 1
