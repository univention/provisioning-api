import uuid

import httpx
import pytest

from consumer.messages.api import v1_prefix as messages_api_prefix
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.main import app as messages_app
from consumer.main import app as subscriptions_app

REALM = "foo"
TOPIC = "bar/baz"
BODY = {"hello": "world"}


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
class TestDispatcher:
    async def test_post_message(
        self,
        messages_client: httpx.AsyncClient,
        subscriptions_client: httpx.AsyncClient,
    ):
        name = str(uuid.uuid4())
        response = await subscriptions_client.post(
            f"{subscriptions_api_prefix}/subscription/",
            json={
                "name": name,
                "realms_topics": [[REALM, TOPIC]],
                "fill_queue": False,
            },
        )
        assert response.status_code == 201

        response = await messages_client.post(
            f"{messages_api_prefix}/message/",
            json={
                "realm": REALM,
                "topic": TOPIC,
                "body": BODY,
            },
        )
        assert response.status_code == 202

    async def test_get_message(
        self,
        messages_client: httpx.AsyncClient,
        subscriptions_client: httpx.AsyncClient,
    ):
        name = str(uuid.uuid4())
        response = await subscriptions_client.post(
            f"{subscriptions_api_prefix}/subscription/",
            json={
                "name": name,
                "realms_topics": [[REALM, TOPIC]],
                "fill_queue": False,
            },
        )
        assert response.status_code == 201

        response = await messages_client.get(
            f"{messages_api_prefix}/subscription/{name}/message"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["data"]["realm"] == REALM
        assert data[0]["data"]["topic"] == TOPIC
        assert data[0]["data"]["body"] == BODY
        assert data[0]["data"]["publisher_name"] == "127.0.0.1"

    async def test_delete_message(
        self,
        messages_client: httpx.AsyncClient,
        subscriptions_client: httpx.AsyncClient,
    ):
        name = str(uuid.uuid4())

        response = await subscriptions_client.post(
            f"{subscriptions_api_prefix}/subscription/",
            json={
                "name": name,
                "realms_topics": [[REALM, TOPIC]],
                "fill_queue": False,
            },
        )
        assert response.status_code == 201

        nats_msg = {
            "subject": "subscriber_2",
            "reply": "$JS.ACK.stream:subscriber_2.durable_name:subscriber_2.4.8.19.1699615014739091916.0",
            "data": {
                "publisher_name": "127.0.0.1",
                "ts": "2023-11-10T11:16:54.704547",
                "realm": "test_realm",
                "topic": "test_topic",
                "body": {"key": "value_1"},
            },
            "headers": {"Nats-Expected-Stream": "stream:subscriber_2"},
        }
        response = await messages_client.post(
            f"{messages_api_prefix}/subscription/{name}/message/",
            json={"msg": nats_msg, "report": {"status": "ok"}},
        )
        assert response.status_code == 200
