# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import base64
import logging

import pytest
from pytest_httpserver import HTTPServer

from univention.provisioning.consumer.admin import (
    AdminClient,
    ProvisioningApiError,
    SubscriptionConflict,
    SubscriptionCreation,
)
from univention.provisioning.models.subscription import NewSubscription, RealmTopic

SUBSCRIPTION = NewSubscription(
    name="portal-consumer",
    realms_topics=[RealmTopic(realm="udm", topic="users/user")],
    request_prefill=True,
    password="consumer-secret-pw",
)


@pytest.fixture
async def client(httpserver: HTTPServer):
    async with AdminClient(httpserver.url_for("/"), "admin", "admin-pw") as client:
        yield client


@pytest.mark.parametrize(
    "status,expected", [(201, SubscriptionCreation.CREATED), (200, SubscriptionCreation.UNCHANGED)]
)
async def test_create_subscription(httpserver: HTTPServer, client, status, expected):
    auth = "Basic " + base64.b64encode(b"admin:admin-pw").decode()
    httpserver.expect_request(
        "/v1/subscriptions", method="POST", headers={"Authorization": auth}, json=SUBSCRIPTION.model_dump()
    ).respond_with_data(status=status)

    assert await client.create_subscription(SUBSCRIPTION) is expected


async def test_conflict(httpserver: HTTPServer, client):
    httpserver.expect_request("/v1/subscriptions", method="POST").respond_with_json({"detail": "differs"}, status=409)

    with pytest.raises(SubscriptionConflict) as error:
        await client.create_subscription(SUBSCRIPTION)
    assert error.value.status == 409
    assert "differs" in error.value.body


@pytest.mark.parametrize("status", [401, 422, 500])
async def test_other_errors(httpserver: HTTPServer, client, status):
    httpserver.expect_request("/v1/subscriptions", method="POST").respond_with_data("x" * 5000, status=status)

    with pytest.raises(ProvisioningApiError) as error:
        await client.create_subscription(SUBSCRIPTION)
    assert not isinstance(error.value, SubscriptionConflict)
    assert error.value.status == status
    assert len(error.value.body) == 1000


async def test_base_url_with_path_and_slash(httpserver: HTTPServer):
    httpserver.expect_request("/provisioning/v1/subscriptions", method="POST").respond_with_data(status=201)

    async with AdminClient(httpserver.url_for("/provisioning/"), "admin", "admin-pw") as client:
        assert await client.create_subscription(SUBSCRIPTION) is SubscriptionCreation.CREATED


async def test_password_not_logged(httpserver: HTTPServer, client, caplog):
    caplog.set_level(logging.DEBUG)
    httpserver.expect_request("/v1/subscriptions", method="POST").respond_with_data(status=201)

    await client.create_subscription(SUBSCRIPTION)

    assert "portal-consumer" in caplog.text
    assert "consumer-secret-pw" not in caplog.text
    assert "admin-pw" not in caplog.text


async def test_get_subscriptions(httpserver: HTTPServer, client):
    httpserver.expect_request("/v1/subscriptions", method="GET").respond_with_json(
        [
            {
                "name": "portal-consumer",
                "realms_topics": [{"realm": "udm", "topic": "users/user"}],
                "request_prefill": True,
                "prefill_queue_status": "done",
            }
        ]
    )

    [subscription] = await client.get_subscriptions()
    assert subscription.name == "portal-consumer"
