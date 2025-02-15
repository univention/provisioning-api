# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Callable

import httpx
import pytest
from test_helpers.mock_data import NATS_SERVER

from univention.provisioning.backends.mocks import MockNatsKVAdapter, MockNatsMQAdapter
from univention.provisioning.rest.config import AppSettings
from univention.provisioning.rest.dependencies import _kv_dependency, _mq_dependency
from univention.provisioning.rest.main import app
from univention.provisioning.rest.mq_adapter_nats import NatsMessageQueue
from univention.provisioning.rest.mq_port import MessageQueuePort
from univention.provisioning.rest.subscriptions_db_adapter_nats import NatsSubscriptionsDB
from univention.provisioning.rest.subscriptions_db_port import SubscriptionsDBPort

_CREDENTIALS = {"username": "dev-user", "password": "dev-password"}


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
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
def fake_app_settings() -> AppSettings:
    return AppSettings(nats_user="api", nats_password="apipass")


@pytest.fixture
async def kv_fake_dependency(fake_app_settings, mock_nats_kv_adapter) -> Callable[[], SubscriptionsDBPort]:
    kv = NatsSubscriptionsDB(fake_app_settings)
    kv.kv = mock_nats_kv_adapter
    return lambda: kv


@pytest.fixture
async def mq_fake_dependency(fake_app_settings, mock_nats_mq_adapter) -> Callable[[], MessageQueuePort]:
    mq = NatsMessageQueue(fake_app_settings)
    mq.mq = mock_nats_mq_adapter
    return lambda: mq


@pytest.fixture(autouse=True)
def override_dependencies(kv_fake_dependency, mq_fake_dependency):
    # Override original port
    # app.dependency_overrides[AppSettingsDep] = settings_mock
    app.dependency_overrides[_kv_dependency] = kv_fake_dependency
    app.dependency_overrides[_mq_dependency] = mq_fake_dependency
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
