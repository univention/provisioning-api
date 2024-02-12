# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import httpx
import pytest

from tests.conftest import (
    REALMS_TOPICS_STR,
    SUBSCRIPTION_NAME,
    CREDENTIALS,
)
from shared.models.subscription import FillQueueStatus
from admin.api import v1_prefix as api_prefix
from consumer.main import app as subscriptions_app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def subscriptions_client():
    async with httpx.AsyncClient(
        app=subscriptions_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.anyio
class TestAdmin:
    async def test_create_subscription(self, subscriptions_client: httpx.AsyncClient):
        name = str(uuid.uuid4())
        response = await subscriptions_client.post(
            f"{api_prefix}/subscriptions",
            json={
                "name": name,
                "realms_topics": [["foo", "bar"]],
                "request_prefill": False,
            },
            auth=(CREDENTIALS.username, CREDENTIALS.password),
        )
        assert response.status_code == 201

    async def test_get_subscriptions(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.get(
            f"{api_prefix}/subscriptions",
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
