# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid
import pytest

import shared.client

from tests.conftest import (
    REALM_TOPIC,
    REALM,
    TOPIC,
)


@pytest.fixture
def provisioning_client() -> shared.client.AsyncClient:
    return shared.client.AsyncClient("http://localhost:7777")


@pytest.fixture
async def simple_subscription(provisioning_client: shared.client.AsyncClient):
    subscriber_name = str(uuid.uuid4())
    await provisioning_client.create_subscription(
        name=subscriber_name,
        realm_topic=REALM_TOPIC,
        fill_queue=False,
    )

    yield subscriber_name

    await provisioning_client.cancel_subscription(subscriber_name, REALM, TOPIC)


async def test_create_subscription(
    provisioning_client: shared.client.AsyncClient, simple_subscription
):
    response = await provisioning_client.get_subscription(simple_subscription)
    assert response


async def test_get_empty_messages(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        count=1,
        timeout=1,
    )

    assert response == []


async def test_get_real_messages(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=1,
    )

    assert response == []


@pytest.mark.xfail()
async def test_get_messages_timeout_zero(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=0,
    )

    assert response == []
