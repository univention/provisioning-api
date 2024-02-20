# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from tests.conftest import FLAT_MESSAGE, CREDENTIALS

from app.internal.api import v1_prefix as api_prefix
from app.main import app, internal_app_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def settings_mock() -> AsyncMock:
    settings = patch("app.internal.api.v1.api.settings").start()
    settings.udm_producer_username = CREDENTIALS.username
    settings.udm_producer_password = CREDENTIALS.password
    return settings


@pytest.mark.anyio
class TestInternalApi:
    async def test_add_event(self, client: httpx.AsyncClient, settings_mock):
        response = await client.post(
            f"{internal_app_path}{api_prefix}/events",
            json=FLAT_MESSAGE,
            auth=(CREDENTIALS.username, CREDENTIALS.password),
        )
        assert response.status_code == 202
