# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import uuid

import httpx
import pytest

from server.core.app.config import app_settings
from univention.provisioning.models.subscription import FillQueueStatus

from ..mock_data import (
    CONSUMER_PASSWORD,
    FLAT_BODY,
    GROUPS_TOPIC,
    PUBLISHER_NAME,
    REALM,
    REALM_TOPIC,
    REALMS_TOPICS_STR,
    REPORT,
    REPORT_SEQ_ID,
    SUBSCRIPTION_NAME,
)


@pytest.mark.anyio
class TestSubscriptionsRoute:
    settings = app_settings()
    subscriptions_url = "/v1/subscriptions"

    async def test_create_subscription(self, client: httpx.AsyncClient):
        name = str(uuid.uuid4())
        response = await client.post(
            self.subscriptions_url,
            json={
                "name": name,
                "realms_topics": [["foo", "bar"]],
                "request_prefill": False,
                "password": "password",
            },
            auth=(self.settings.admin_username, self.settings.admin_password),
        )
        assert response.status_code == 201

    async def test_create_subscription_existing_subscription(self, client: httpx.AsyncClient):
        response = await client.post(
            self.subscriptions_url,
            json={
                "name": SUBSCRIPTION_NAME,
                "realms_topics": [REALM_TOPIC],
                "request_prefill": True,
                "password": "password",
            },
            auth=(self.settings.admin_username, self.settings.admin_password),
        )
        assert response.status_code == 200

    async def test_create_subscription_existing_subscription_different_parameters(self, client: httpx.AsyncClient):
        response = await client.post(
            self.subscriptions_url,
            json={
                "name": SUBSCRIPTION_NAME,
                "realms_topics": [["foo", "bar"]],
                "request_prefill": False,
                "password": "password",
            },
            auth=(self.settings.admin_username, self.settings.admin_password),
        )
        assert response.status_code == 409

    async def test_get_subscriptions(self, client: httpx.AsyncClient):
        response = await client.get(
            self.subscriptions_url, auth=(self.settings.admin_username, self.settings.admin_password)
        )
        assert response.status_code == 200
        data = response.json()
        assert data[0]["name"] == SUBSCRIPTION_NAME
        assert data[0]["request_prefill"]
        assert data[0]["prefill_queue_status"] == FillQueueStatus.done
        assert len(data[0]["realms_topics"]) == len([REALMS_TOPICS_STR])
        assert all((realm_topic in data[0]["realms_topics"] for realm_topic in [REALMS_TOPICS_STR]))

    async def test_get_subscription(self, client: httpx.AsyncClient):
        response = await client.get(
            f"{self.subscriptions_url}/{SUBSCRIPTION_NAME}", auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == SUBSCRIPTION_NAME
        assert data["request_prefill"]
        assert data["prefill_queue_status"] == FillQueueStatus.done
        assert len(data["realms_topics"]) == len([REALMS_TOPICS_STR])
        assert all((realm_topic in data["realms_topics"] for realm_topic in [REALMS_TOPICS_STR]))

    async def test_delete_subscription(self, client: httpx.AsyncClient):
        response = await client.delete(
            f"{self.subscriptions_url}/{SUBSCRIPTION_NAME}",
            auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD),
        )
        assert response.status_code == 200

    async def test_delete_subscription_as_admin(self, client: httpx.AsyncClient):
        response = await client.delete(
            f"{self.subscriptions_url}/{SUBSCRIPTION_NAME}",
            auth=(self.settings.admin_username, self.settings.admin_password),
        )
        assert response.status_code == 200

    async def test_get_message(self, client: httpx.AsyncClient):
        response = await client.get(
            f"{self.subscriptions_url}/{SUBSCRIPTION_NAME}/messages/next", auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD)
        )
        assert response.status_code == 200
        data = response.json()
        assert data["realm"] == REALM
        assert data["topic"] == GROUPS_TOPIC
        assert data["body"] == FLAT_BODY
        assert data["publisher_name"] == PUBLISHER_NAME
        assert data["sequence_number"] == 1

    async def test_update_messages_status(self, client: httpx.AsyncClient):
        response = await client.patch(
            f"{self.subscriptions_url}/{SUBSCRIPTION_NAME}/messages/{REPORT_SEQ_ID}/status",
            json=REPORT.model_dump(),
            auth=(SUBSCRIPTION_NAME, CONSUMER_PASSWORD),
        )
        assert response.status_code == 200
