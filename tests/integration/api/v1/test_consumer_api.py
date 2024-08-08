# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch

import httpx
import pytest

from server.core.app.consumer.messages.api import v1_prefix as messages_api_prefix
from server.core.app.consumer.subscriptions.api import v1_prefix as api_prefix
from server.core.app.main import app as messages_app
from server.core.app.main import app as subscriptions_app
from univention.provisioning.models.subscription import FillQueueStatus

from tests.conftest import (
    CONSUMER_PASSWORD,
    CREDENTIALS,
    FLAT_BODY,
    PUBLISHER_NAME,
    REALM,
    REALMS_TOPICS_STR,
    REPORT,
    SUBSCRIPTION_NAME,
    TOPIC,
)


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def subscriptions_client():
    async with httpx.AsyncClient(app=subscriptions_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
async def messages_client():
    async with httpx.AsyncClient(app=messages_app, base_url="http://testserver") as client:
        yield client


@pytest.fixture
def settings_mock() -> AsyncMock:
    settings = patch("server.core.app.auth.app_settings").start()
    settings.admin_username = CREDENTIALS.username
    settings.admin_password = CREDENTIALS.password
    return settings


@pytest.mark.anyio
class TestConsumer:
    async def test_get_subscription(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.get(
            f"{api_prefix}/subscriptions/{SUBSCRIPTION_NAME}",
            auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == SUBSCRIPTION_NAME
        assert data["request_prefill"]
        assert data["prefill_queue_status"] == FillQueueStatus.done
        assert len(data["realms_topics"]) == len([REALMS_TOPICS_STR])
        assert all((realm_topic in data["realms_topics"] for realm_topic in [REALMS_TOPICS_STR]))

    async def test_delete_subscription(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.delete(
            f"{api_prefix}/subscriptions/{SUBSCRIPTION_NAME}",
            auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD),
        )
        assert response.status_code == 200

    async def test_delete_subscription_as_admin(self, subscriptions_client: httpx.AsyncClient, settings_mock):
        response = await subscriptions_client.delete(
            f"{api_prefix}/subscriptions/{SUBSCRIPTION_NAME}",
            auth=(CREDENTIALS.username, CREDENTIALS.password),
        )
        assert response.status_code == 200

    async def test_get_message(
        self,
        messages_client: httpx.AsyncClient,
    ):
        response = await messages_client.get(
            f"{messages_api_prefix}/subscriptions/{SUBSCRIPTION_NAME}/messages",
            auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["realm"] == REALM
        assert data["topic"] == TOPIC
        assert data["body"] == FLAT_BODY
        assert data["publisher_name"] == PUBLISHER_NAME
        assert data["sequence_number"] == 1

    async def test_post_messages_status(
        self,
        messages_client: httpx.AsyncClient,
    ):
        response = await messages_client.post(
            f"{messages_api_prefix}/subscriptions/{SUBSCRIPTION_NAME}/messages-status",
            json=REPORT.model_dump(),
            auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD),
        )
        assert response.status_code == 200
