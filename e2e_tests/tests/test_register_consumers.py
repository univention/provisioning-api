# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

"""
The register-consumers entry point against a real Provisioning API.

A small aiohttp app stands in for the Kubernetes API, so the `kubernetes_secret`
reference is resolved over HTTP the way the Job does it in a cluster.
"""

import base64
import json
import logging
import uuid
from pathlib import Path

import pytest
from aiohttp import web

from univention.provisioning.consumer.api import ProvisioningConsumerClient, ProvisioningConsumerClientSettings
from univention.provisioning.consumer.kubernetes_secrets import KubernetesSecretReader
from univention.provisioning.consumer.register import RegisterConsumersSettings, register_all

from .conftest import _wait_until_subscription_is_dispatched
from .e2e_settings import E2ETestSettings
from .mock_data import DUMMY_REALMS_TOPICS

NAMESPACE = "e2e"
TOKEN = "e2e-service-account-token"


class FakeKubernetesApi:
    def __init__(self):
        self.secrets: dict[str, dict[str, str]] = {}
        self.url = ""
        self._runner: web.AppRunner | None = None

    def set_secret(self, name: str, key: str, value: str):
        self.secrets.setdefault(name, {})[key] = base64.b64encode(value.encode()).decode()

    async def handle(self, request: web.Request) -> web.Response:
        if request.headers.get("Authorization") != f"Bearer {TOKEN}":
            return web.json_response({"reason": "Unauthorized"}, status=401)
        name = request.match_info["name"]
        if request.match_info["namespace"] != NAMESPACE or name not in self.secrets:
            return web.json_response({"reason": "NotFound"}, status=404)
        return web.json_response({"metadata": {"name": name}, "data": self.secrets[name]})

    async def start(self):
        app = web.Application()
        app.router.add_get("/api/v1/namespaces/{namespace}/secrets/{name}", self.handle)
        self._runner = web.AppRunner(app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, "127.0.0.1", 0)
        await site.start()
        port = self._runner.addresses[0][1]
        self.url = f"http://127.0.0.1:{port}"

    async def stop(self):
        await self._runner.cleanup()

    def reader(self) -> KubernetesSecretReader:
        return KubernetesSecretReader(self.url, NAMESPACE, TOKEN, ssl_context=None)


@pytest.fixture
async def kubernetes_api():
    api = FakeKubernetesApi()
    await api.start()
    yield api
    await api.stop()


@pytest.fixture
def specs_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture
def settings(test_settings: E2ETestSettings, specs_dir: Path) -> RegisterConsumersSettings:
    return RegisterConsumersSettings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        admin_username=test_settings.provisioning_admin_username,
        admin_password=test_settings.provisioning_admin_password,
        specs_dir=specs_dir,
        retry_delay=0,
    )


@pytest.fixture
def consumer_names() -> dict[str, str]:
    return {"inline": f"e2e-inline-{uuid.uuid4()}", "referenced": f"e2e-referenced-{uuid.uuid4()}"}


@pytest.fixture
async def cleanup_subscriptions(consumer_names, provisioning_admin_client):
    yield
    for name in consumer_names.values():
        await provisioning_admin_client.cancel_subscription(name)


def write_spec(specs_dir: Path, filename: str, name: str, password):
    spec = {
        "name": name,
        "realms_topics": [rt.model_dump() for rt in DUMMY_REALMS_TOPICS],
        "request_prefill": False,
        "password": password,
    }
    (specs_dir / f"{filename}.json").write_text(json.dumps(spec))


async def test_register_consumers_with_inline_and_referenced_passwords(
    test_settings: E2ETestSettings,
    settings: RegisterConsumersSettings,
    specs_dir: Path,
    kubernetes_api: FakeKubernetesApi,
    consumer_names: dict[str, str],
    cleanup_subscriptions,
    caplog,
):
    caplog.set_level(logging.INFO)
    referenced_password = str(uuid.uuid4())
    kubernetes_api.set_secret("referenced-consumer", "password", referenced_password)
    write_spec(specs_dir, "inline", consumer_names["inline"], str(uuid.uuid4()))
    write_spec(
        specs_dir,
        "referenced",
        consumer_names["referenced"],
        {"kubernetes_secret": {"name": "referenced-consumer", "key": "password"}},
    )

    assert await register_all(settings, kubernetes_api.reader) == 0
    assert "2 created, 0 unchanged, 0 failed" in caplog.text

    # The consumer authenticates with the password from the Secret and receives messages.
    consumer_settings = ProvisioningConsumerClientSettings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        provisioning_api_username=consumer_names["referenced"],
        provisioning_api_password=referenced_password,
        log_level="INFO",
    )
    async with ProvisioningConsumerClient(consumer_settings) as consumer:
        await _wait_until_subscription_is_dispatched(
            consumer, consumer_names["referenced"], DUMMY_REALMS_TOPICS, test_settings
        )

    # A rerun of the Job, as on every Helm upgrade, changes nothing.
    caplog.clear()
    assert await register_all(settings, kubernetes_api.reader) == 0
    assert "0 created, 2 unchanged, 0 failed" in caplog.text

    # A rotated password is rejected with an explanation.
    kubernetes_api.set_secret("referenced-consumer", "password", str(uuid.uuid4()))
    caplog.clear()
    assert await register_all(settings, kubernetes_api.reader) == 1
    assert "0 created, 1 unchanged, 1 failed" in caplog.text
    assert "already exists with a different password or config" in caplog.text
    assert referenced_password not in caplog.text
