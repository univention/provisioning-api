# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import httpx
import pytest

from consumer.messages.api import v1_prefix as messages_api_prefix
from tests.conftest import (
    REALMS_TOPICS_STR,
    REALM,
    TOPIC,
    PUBLISHER_NAME,
    BODY,
    FLAT_MESSAGE,
    SUBSCRIPTION_NAME,
)
from shared.models.subscription import FillQueueStatus
from consumer.subscriptions.api import v1_prefix as api_prefix
from consumer.main import app as messages_app
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


@pytest.fixture(scope="session")
async def messages_client():
    async with httpx.AsyncClient(
        app=messages_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.anyio
class TestConsumer:
    async def test_create_subscription(self, subscriptions_client: httpx.AsyncClient):
        name = str(uuid.uuid4())
        response = await subscriptions_client.post(
            f"{api_prefix}/subscriptions",
            json={
                "name": name,
                "realms_topics": [["foo", "bar"]],
                "request_prefill": False,
            },
        )
        assert response.status_code == 201

    async def test_get_subscription(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.get(
            f"{api_prefix}/subscriptions/{SUBSCRIPTION_NAME}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == SUBSCRIPTION_NAME
        assert data["request_prefill"]
        assert data["prefill_queue_status"] == FillQueueStatus.done
        assert len(data["realms_topics"]) == len([REALMS_TOPICS_STR])
        assert all(
            (
                realm_topic in data["realms_topics"]
                for realm_topic in [REALMS_TOPICS_STR]
            )
        )

    async def test_delete_subscription(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.delete(
            f"{api_prefix}/subscriptions/{SUBSCRIPTION_NAME}",
        )
        assert response.status_code == 200

    async def test_get_message(
        self,
        messages_client: httpx.AsyncClient,
    ):
        response = await messages_client.get(
            f"{messages_api_prefix}/subscriptions/{SUBSCRIPTION_NAME}/messages"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["data"]["realm"] == REALM
        assert data[0]["data"]["topic"] == TOPIC
        assert data[0]["data"]["body"] == BODY
        assert data[0]["data"]["publisher_name"] == PUBLISHER_NAME

    async def test_post_message_status(
        self,
        messages_client: httpx.AsyncClient,
    ):
        nats_msg = {
            "subject": SUBSCRIPTION_NAME,
            "reply": (
                f"$JS.ACK.stream:{SUBSCRIPTION_NAME}.durable_name:{SUBSCRIPTION_NAME}.4.8.19.1699615014739091916.0"
            ),
            "data": FLAT_MESSAGE,
            "headers": {"Nats-Expected-Stream": f"stream:{SUBSCRIPTION_NAME}"},
        }
        response = await messages_client.post(
            f"{messages_api_prefix}/subscriptions/{SUBSCRIPTION_NAME}/messages-status",
            json={"msg": nats_msg, "report": {"status": "ok"}},
        )
        assert response.status_code == 200
