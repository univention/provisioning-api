# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from fastapi.testclient import TestClient
import httpx
import pytest

from tests.conftest import REALM, TOPIC, BODY, FLAT_MESSAGE, SUBSCRIBER_NAME
from events.api import v1_prefix as events_api_prefix
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.messages.api import v1_prefix as messages_api_prefix
from consumer.main import app


@pytest.fixture(scope="session")
async def producer():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
async def consumer():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
async def test_udm_create_user_event_is_routed_correctly(
    producer: httpx.AsyncClient,
    consumer: httpx.AsyncClient,
):
    # register a consumer
    response = await consumer.post(
        f"{subscriptions_api_prefix}/subscriptions",
        json={
            "name": SUBSCRIBER_NAME,
            "realm_topic": ["foo", "bar"],
            "request_prefill": False,
        },
    )
    assert response.status_code == 201

    # call event api with new user event
    response = await producer.post(f"{events_api_prefix}/events", json=FLAT_MESSAGE)
    assert response.status_code == 202

    message_consumer = TestClient(app)
    # evaluate that the message about a new user is received by the consumer
    with message_consumer.websocket_connect(
        f"{messages_api_prefix}/subscriptions/{SUBSCRIBER_NAME}/ws"
    ) as ws_client:
        data = ws_client.receive_json()

        assert data["realm"] == REALM
        assert data["topic"] == TOPIC
        assert data["body"] == BODY
