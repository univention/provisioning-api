import uuid

import httpx
import pytest

from consumer.messages.api import v1_prefix as api_prefix
from consumer.main import app as dispatcher_app
from consumer.main import app as consumer_app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def consumer_client():
    async with httpx.AsyncClient(
        app=consumer_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture(scope="session")
async def dispatcher_client():
    async with httpx.AsyncClient(
        app=dispatcher_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.anyio
async def test_post_message(
    dispatcher_client: httpx.AsyncClient, consumer_client: httpx.AsyncClient
):
    name = str(uuid.uuid4())
    realm = "foo"
    topic = "bar/baz"
    body = {
        "string": "text",
        "number": 1,
        "list": [1, "2"],
        "obj": {
            "value": "ok",
        },
    }
    body = {"hello": "world"}

    response = await consumer_client.post(
        f"{api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": [[realm, topic]],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = await dispatcher_client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body,
        },
    )
    assert response.status_code == 202

    response = await consumer_client.get(f"{api_prefix}/subscription/{name}/message")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0][1]["realm"] == realm
    assert data[0][1]["topic"] == topic
    assert data[0][1]["body"] == body


@pytest.mark.anyio
async def test_manual_message_processing(
    dispatcher_client: httpx.AsyncClient, consumer_client: httpx.AsyncClient
):
    name = str(uuid.uuid4())
    realm = "foo"
    topic = "bar/baz"
    body1 = {"first": {"foo": "1"}}
    body2 = {"second": {"bar": "2"}}

    response = await consumer_client.post(
        f"{api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": [[realm, topic]],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = await dispatcher_client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body1,
        },
    )
    assert response.status_code == 202

    response = await dispatcher_client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body2,
        },
    )
    assert response.status_code == 202

    response = await consumer_client.get(f"{api_prefix}/subscription/{name}/message")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0][1]["body"] == body1
    message_id: str = data[0][0]

    response = await dispatcher_client.post(
        f"{api_prefix}/subscription/{name}/message/{message_id}",
        json={
            "status": "ok",
        },
    )
    assert response.status_code == 200

    response = await consumer_client.get(f"{api_prefix}/subscription/{name}/message")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0][1]["body"] == body2
