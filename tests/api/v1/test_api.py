import uuid

from httpx import AsyncClient
import pytest

from core.models.subscriber import FillQueueStatus
from dispatcher.main import app
from dispatcher.api import v1_prefix as api_prefix


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
async def test_create_and_get_subscription(client: AsyncClient):
    name = str(uuid.uuid4())
    realms_topics = [
        ["foo", "bar/baz"],
        ["abc", "def/ghi"],
    ]

    response = await client.post(
        f"{api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": realms_topics,
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = await client.get(f"{api_prefix}/subscription/{name}")
    assert response.status_code == 200
    data = response.json()
    import json

    print(json.dumps(data, indent=2))
    assert data["name"] == name
    assert not data["fill_queue"]
    assert data["fill_queue_status"] == FillQueueStatus.done
    assert len(data["realms_topics"]) == len(realms_topics)
    assert all(
        ([realm, topic] in data["realms_topics"] for realm, topic in realms_topics)
    )


@pytest.mark.anyio
async def test_get_subscriptions(client: AsyncClient):
    subscriptions = [
        {
            "name": str(uuid.uuid4()),
            "realms_topics": [
                ["foo", "bar/baz"],
                ["abc", "def/ghi"],
            ],
        },
        {
            "name": str(uuid.uuid4()),
            "realms_topics": [
                ["foo", "f33d/f00d"],
                ["bar", "c0ff/ee"],
            ],
        },
    ]

    for sub in subscriptions:
        response = await client.post(
            f"{api_prefix}/subscription/",
            json={
                "name": sub["name"],
                "realms_topics": sub["realms_topics"],
                "fill_queue": False,
            },
        )
        assert response.status_code == 201

    response = await client.get(f"{api_prefix}/subscription/")
    assert response.status_code == 200
    data = response.json()

    for request in subscriptions:
        ok = False
        for returned in data:
            if returned["name"] != request["name"]:
                continue

            assert len(returned["realms_topics"]) == len(request["realms_topics"])
            assert all(
                (
                    [realm, topic] in returned["realms_topics"]
                    for realm, topic in request["realms_topics"]
                )
            )

            ok = True

        assert ok


@pytest.mark.anyio
async def test_delete_subscription(client: AsyncClient):
    name = str(uuid.uuid4())
    realms_topics = [
        ["foo", "bar/baz"],
        ["abc", "def/ghi"],
    ]

    response = await client.post(
        f"{api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": realms_topics,
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = await client.get(f"{api_prefix}/subscription/{name}")
    assert response.status_code == 200
    assert response.json()["name"] == name

    response = await client.delete(f"{api_prefix}/subscription/{name}")
    assert response.status_code == 200

    response = await client.get(f"{api_prefix}/subscription/{name}")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_post_message(client: AsyncClient):
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

    response = await client.post(
        f"{api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": [[realm, topic]],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = await client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body,
        },
    )
    assert response.status_code == 202

    response = await client.get(f"{api_prefix}/subscription/{name}/message")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0][1]["realm"] == realm
    assert data[0][1]["topic"] == topic
    assert data[0][1]["body"] == body


@pytest.mark.anyio
async def test_manual_message_processing(client: AsyncClient):
    name = str(uuid.uuid4())
    realm = "foo"
    topic = "bar/baz"
    body1 = {"first": {"foo": "1"}}
    body2 = {"second": {"bar": "2"}}

    response = await client.post(
        f"{api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": [[realm, topic]],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = await client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body1,
        },
    )
    assert response.status_code == 202

    response = await client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body2,
        },
    )
    assert response.status_code == 202

    response = await client.get(f"{api_prefix}/subscription/{name}/message")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0][1]["body"] == body1
    message_id: str = data[0][0]

    response = await client.post(
        f"{api_prefix}/subscription/{name}/message/{message_id}",
        json={
            "status": "ok",
        },
    )
    assert response.status_code == 200

    response = await client.get(f"{api_prefix}/subscription/{name}/message")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0][1]["body"] == body2
