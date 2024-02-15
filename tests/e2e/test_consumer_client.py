# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid
import pytest
import requests

import shared.client
from shared.config import settings
from shared.models.api import MessageProcessingStatus
import shared.models.queue

from tests.conftest import (
    REALM,
    TOPIC,
    REALMS_TOPICS,
)
from univention.admin.rest.client import UDM


@pytest.fixture
def provisioning_client() -> shared.client.AsyncClient:
    return shared.client.AsyncClient("http://localhost:7777")


@pytest.fixture
async def simple_subscription(provisioning_client: shared.client.AsyncClient):
    subscriber_name = str(uuid.uuid4())

    response = requests.post(
        "http://localhost:7777/admin/v1/subscriptions",
        json={
            "name": subscriber_name,
            "realms_topics": REALMS_TOPICS,
            "request_prefill": False,
            "password": "password",
        },
        auth=(settings.admin_username, settings.admin_password),
    )
    assert response.status_code == 201

    yield subscriber_name

    await provisioning_client.cancel_subscription(subscriber_name)


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


async def test_send_message(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    requests.post(
        "http://localhost:7777/events/v1/events",
        json={
            "publisher_name": "consumer_client_tests",
            "ts": "2024-02-07T09:01:33.835Z",
            "realm": REALM,
            "topic": TOPIC,
            "body": {"foo": "bar"},
        },
    )

    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        count=1,
        timeout=1,
    )

    assert len(response) == 1
    assert response[0].data["body"]["foo"] == "bar"


@pytest.mark.xfail()
async def test_pop_message(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription, count=1, timeout=1, pop=True
    )

    assert response == []


async def test_get_real_messages(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str, udm: UDM
):
    groups = udm.get(TOPIC)
    assert groups
    group = groups.new()
    group.properties["name"] = str(uuid.uuid1())
    group.save()

    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=5,
    )

    assert len(response) == 1


@pytest.mark.xfail()
async def test_get_messages_zero_timeout(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=0,
    )

    assert response == []


async def test_acknowledge_messages(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str, udm: UDM
):
    groups = udm.get(TOPIC)
    assert groups
    group = groups.new()
    group.properties["name"] = str(uuid.uuid1())
    group.save()

    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=5,
    )

    assert len(response) == 1
    message = response[0]

    response = await provisioning_client.set_message_status(
        simple_subscription,
        message,
        MessageProcessingStatus.ok,
    )
