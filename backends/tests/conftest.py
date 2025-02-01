# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

try:
    from unittest.mock import AsyncMock
except ImportError:
    from mock import AsyncMock
from typing import Dict

import pytest

from univention.provisioning.backends.mocks import MockNatsMQAdapter
from univention.provisioning.testing.mock_data import MSG, NATS_SERVER

_CREDENTIALS = {"username": "dev-user", "password": "dev-password"}


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def nats_credentials() -> Dict[str, str]:
    return _CREDENTIALS


@pytest.fixture
def mock_nats_mq_adapter(nats_credentials) -> MockNatsMQAdapter:
    return MockNatsMQAdapter(
        server=NATS_SERVER, user=nats_credentials["username"], password=nats_credentials["password"]
    )


@pytest.fixture
def mock_fetch(mock_nats_mq_adapter):
    sub = AsyncMock()
    sub.fetch = AsyncMock(return_value=[MSG])
    mock_nats_mq_adapter._js.pull_subscribe = AsyncMock(return_value=sub)
    return sub.fetch
