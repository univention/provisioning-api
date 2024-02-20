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
    CONSUMER_PASSWORD,
)
from univention.admin.rest.client import UDM

SUBSCRIBER_NAME = str(uuid.uuid4())


@pytest.fixture
def provisioning_client() -> shared.client.AsyncClient:
    return shared.client.AsyncClient(
        "http://localhost:7777", SUBSCRIBER_NAME, CONSUMER_PASSWORD
    )


@pytest.fixture
async def simple_subscription(provisioning_client: shared.client.AsyncClient):
    response = requests.post(
        "http://localhost:7777/internal/admin/v1/subscriptions",
        json={
            "name": SUBSCRIBER_NAME,
            "realms_topics": REALMS_TOPICS,
            "request_prefill": False,
            "password": CONSUMER_PASSWORD,
        },
        auth=(settings.admin_username, settings.admin_password),
    )
    assert response.status_code == 201

    yield SUBSCRIBER_NAME

    await provisioning_client.cancel_subscription(SUBSCRIBER_NAME)


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
    response = requests.post(
        "http://localhost:7777/internal/v1/events",
        json={
            "publisher_name": "consumer_client_tests",
            "ts": "2024-02-07T09:01:33.835Z",
            "realm": REALM,
            "topic": TOPIC,
            "body": {"foo": "bar"},
        },
        auth=(settings.udm_producer_username, settings.udm_producer_password),
    )
    assert response.status_code == 202

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
