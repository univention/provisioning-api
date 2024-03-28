# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid
from unittest.mock import AsyncMock, patch
import httpx
import pytest
from tests.conftest import REALMS_TOPICS_STR, SUBSCRIPTION_NAME, CREDENTIALS
from src.shared.models import FillQueueStatus
from src.server.core.app.admin.api import v1_prefix as api_prefix
from src.server.core.app.main import app as subscriptions_app, internal_app_path


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def subscriptions_client():
    async with httpx.AsyncClient(
        app=subscriptions_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture
def settings_mock() -> AsyncMock:
    settings = patch("app.auth.app_settings").start()
    settings.admin_username = CREDENTIALS.username
    settings.admin_password = CREDENTIALS.password
    return settings


@pytest.mark.anyio
class TestAdmin:
    async def test_create_subscription(
        self, subscriptions_client: httpx.AsyncClient, settings_mock
    ):
        name = str(uuid.uuid4())
        response = await subscriptions_client.post(
            f"{internal_app_path}{api_prefix}/subscriptions",
            json={
                "name": name,
                "realms_topics": [["foo", "bar"]],
                "request_prefill": False,
                "password": "password",
            },
            auth=(CREDENTIALS.username, CREDENTIALS.password),
        )
        assert response.status_code == 201

    async def test_get_subscriptions(
        self, subscriptions_client: httpx.AsyncClient, settings_mock
    ):
        response = await subscriptions_client.get(
            f"{internal_app_path}{api_prefix}/subscriptions",
            auth=(CREDENTIALS.username, CREDENTIALS.password),
        )
        assert response.status_code == 200
        data = response.json()
        assert data[0]["name"] == SUBSCRIPTION_NAME
        assert data[0]["request_prefill"]
        assert data[0]["prefill_queue_status"] == FillQueueStatus.done
        assert len(data[0]["realms_topics"]) == len([REALMS_TOPICS_STR])
        assert all(
            (
                realm_topic in data[0]["realms_topics"]
                for realm_topic in [REALMS_TOPICS_STR]
            )
        )
