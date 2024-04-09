# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch
import httpx
import pytest
from fastapi.testclient import TestClient
from tests.conftest import REALM, TOPIC, BODY, FLAT_MESSAGE, CREDENTIALS
from tests.conftest import SUBSCRIPTION_NAME
from server.core.app.consumer.messages.api import v1_prefix as messages_api_prefix
from server.core.app.internal.api import v1_prefix as api_prefix
from server.core.app.main import app, internal_app_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
def settings_mock() -> AsyncMock:
    settings = patch("server.core.app.internal.api.v1.api.app_settings").start()
    settings.events_username_udm = CREDENTIALS.username
    settings.events_password_udm = CREDENTIALS.password
    return settings


@pytest.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
async def test_websocket(settings_mock, client: httpx.AsyncClient):
    client = TestClient(app)

    response = client.post(
        f"{internal_app_path}{api_prefix}/events",
        json=FLAT_MESSAGE,
        auth=(CREDENTIALS.username, CREDENTIALS.password),
    )
    assert response.status_code == 202

    with client.websocket_connect(
        f"{messages_api_prefix}/subscriptions/{SUBSCRIPTION_NAME}/ws",
    ) as ws_client:
        data = ws_client.receive_json()

        assert data["realm"] == REALM
        assert data["topic"] == TOPIC
        assert data["body"] == BODY
