# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Callable

import httpx
import pytest

from univention.provisioning.backends.mocks import MockNatsKVAdapter, MockNatsMQAdapter
from univention.provisioning.rest.config import AppSettings
from univention.provisioning.rest.main import app
from univention.provisioning.rest.port import Port
from univention.provisioning.testing.mock_data import NATS_SERVER

pytest_plugins = ["univention.provisioning.testing.conftest"]

_CREDENTIALS = {"username": "dev-user", "password": "dev-password"}


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
def nats_credentials() -> dict[str, str]:
    return _CREDENTIALS


@pytest.fixture
def mock_nats_kv_adapter(nats_credentials) -> MockNatsKVAdapter:
    return MockNatsKVAdapter(
        server=NATS_SERVER, user=nats_credentials["username"], password=nats_credentials["password"]
    )


@pytest.fixture
def mock_nats_mq_adapter(nats_credentials) -> MockNatsMQAdapter:
    return MockNatsMQAdapter(
        server=NATS_SERVER, user=nats_credentials["username"], password=nats_credentials["password"]
    )


@pytest.fixture
async def port_fake_dependency(mock_nats_kv_adapter, mock_nats_mq_adapter) -> Callable[[], Port]:
    port = Port(AppSettings(nats_user="api", nats_password="apipass"))
    port.mq_adapter = mock_nats_mq_adapter
    port.kv_adapter = mock_nats_kv_adapter
    return lambda: port


@pytest.fixture(autouse=True)
def override_dependencies(port_fake_dependency):
    # Override original port
    # app.dependency_overrides[AppSettingsDep] = settings_mock
    app.dependency_overrides[Port.port_dependency] = port_fake_dependency
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
