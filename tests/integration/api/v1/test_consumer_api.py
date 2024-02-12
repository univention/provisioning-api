# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

import httpx
import pytest


from consumer.messages.api import v1_prefix as messages_api_prefix
from tests.conftest import (
    REALMS_TOPICS_STR,
    REALM,
    TOPIC,
    PUBLISHER_NAME,
    BODY,
    SUBSCRIBER_NAME,
    REPORT,
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
            f"{api_prefix}/subscriptions",
            json={
                "name": SUBSCRIBER_NAME,
                "realm_topic": ["foo", "bar"],
                "request_prefill": False,
            },
        )
        assert response.status_code == 201

    async def test_get_subscription(self, subscriptions_client: httpx.AsyncClient):
        response = await subscriptions_client.get(
            f"{api_prefix}/subscriptions/{SUBSCRIBER_NAME}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == SUBSCRIBER_NAME
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
            f"{api_prefix}/subscriptions/{SUBSCRIBER_NAME}?realm={REALM}&topic={TOPIC}",
        )
        assert response.status_code == 200

    async def test_get_message(
        self,
        messages_client: httpx.AsyncClient,
    ):
        response = await messages_client.get(
            f"{messages_api_prefix}/subscriptions/{SUBSCRIBER_NAME}/messages"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["realm"] == REALM
        assert data[0]["topic"] == TOPIC
        assert data[0]["body"] == BODY
        assert data[0]["publisher_name"] == PUBLISHER_NAME
        assert data[0]["sequence_number"] == 1

    async def test_post_message_status(
        self,
        messages_client: httpx.AsyncClient,
    ):
        response = await messages_client.post(
            f"{messages_api_prefix}/subscriptions/{SUBSCRIBER_NAME}/messages",
            json=[REPORT.model_dump()],
        )
        assert response.status_code == 200
