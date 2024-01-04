# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

import httpx
import pytest


from consumer.messages.api import v1_prefix as messages_api_prefix
from tests.conftest import (
    REALMS_TOPICS,
    REALM,
    TOPIC,
    PUBLISHER_NAME,
    BODY,
    FLAT_MESSAGE,
    SUBSCRIBER_NAME,
)
from shared.models.subscriber import FillQueueStatus
from consumer.subscriptions.api import v1_prefix as api_prefix
from consumer.main import app as messages_app
from consumer.main import app as subscriptions_app

logger = logging.getLogger(__name__)


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
        response = await subscriptions_client.post(
            f"{api_prefix}/subscription/",
            json={
                "name": SUBSCRIBER_NAME,
                "realm_topic": ["foo", "bar"],
                "fill_queue": False,
            },
        )
        assert response.status_code == 201

    async def test_get_subscription(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.get(
            f"{api_prefix}/subscription/{SUBSCRIBER_NAME}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == SUBSCRIBER_NAME
        assert data["fill_queue"]
        assert data["fill_queue_status"] == FillQueueStatus.done
        assert len(data["realms_topics"]) == len(REALMS_TOPICS)
        assert all(
            (realm_topic in data["realms_topics"] for realm_topic in REALMS_TOPICS)
        )

    async def test_delete_subscription(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.delete(
            f"{api_prefix}/subscription/{SUBSCRIBER_NAME}?realm={REALM}&topic={TOPIC}",
        )
        assert response.status_code == 200

    async def test_get_message(
        self,
        messages_client: httpx.AsyncClient,
    ):
        response = await messages_client.get(
            f"{messages_api_prefix}/subscription/{SUBSCRIBER_NAME}/message"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["data"]["realm"] == REALM
        assert data[0]["data"]["topic"] == TOPIC
        assert data[0]["data"]["body"] == BODY
        assert data[0]["data"]["publisher_name"] == PUBLISHER_NAME

    async def test_delete_message(
        self,
        messages_client: httpx.AsyncClient,
    ):
        nats_msg = {
            "subject": SUBSCRIBER_NAME,
            "reply": f"$JS.ACK.stream:{SUBSCRIBER_NAME}.durable_name:{SUBSCRIBER_NAME}.4.8.19.1699615014739091916.0",
            "data": FLAT_MESSAGE,
            "headers": {"Nats-Expected-Stream": f"stream:{SUBSCRIBER_NAME}"},
        }
        response = await messages_client.post(
            f"{messages_api_prefix}/subscription/{SUBSCRIBER_NAME}/message/",
            json={"msg": nats_msg, "report": {"status": "ok"}},
        )
        assert response.status_code == 200
