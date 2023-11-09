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
        assert data[0]["realm"] == REALM
        assert data[0]["topic"] == TOPIC
        assert data[0]["body"] == BODY
        assert data[0]["publisher_name"] == "127.0.0.1"

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

        message_id: str = "1"
        response = await messages_client.post(
            f"{messages_api_prefix}/subscription/{name}/message/{message_id}",
            json={
                "status": "ok",
            },
        )
        assert response.status_code == 200
