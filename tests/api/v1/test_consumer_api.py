import uuid

import httpx
import pytest

from shared.models.subscriber import FillQueueStatus
from consumer.subscriptions.api import v1_prefix as api_prefix
from consumer.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
class TestConsumer:
    async def test_create_subscription(
        self, client: httpx.AsyncClient, override_dependencies_without_sub
    ):
        name = str(uuid.uuid4())
        realms_topics = ["foo", "bar/baz"]

        response = await client.post(
            f"{api_prefix}/subscription/",
            json={
                "name": name,
                "realm_topic": realms_topics,
                "fill_queue": False,
            },
        )
        assert response.status_code == 201

    async def test_get_subscription(self, client: httpx.AsyncClient):
        name = "0f084f8c-1093-4024-b215-55fe8631ddf6"
        realms_topics = ["foo:bar", "abc:def"]

        response = await client.get(f"{api_prefix}/subscription/{name}")
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == name
        assert data["fill_queue"]
        assert data["fill_queue_status"] == FillQueueStatus.done
        assert len(data["realms_topics"]) == len(realms_topics)
        assert all(
            (realm_topic in data["realms_topics"] for realm_topic in realms_topics)
        )

    async def test_delete_subscription(self, client: httpx.AsyncClient):
        name = str(uuid.uuid4())

        response = await client.delete(
            f"{api_prefix}/subscription/{name}?realm=foo&topic=bar",
        )
        assert response.status_code == 200
