import httpx
import pytest

from tests.conftest import SUBSCRIBER_NAME
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
    async def test_create_subscription(self, client: httpx.AsyncClient):
        realms_topics = ["abc", "def"]

        response = await client.post(
            f"{api_prefix}/subscription/",
            json={
                "name": SUBSCRIBER_NAME,
                "realm_topic": realms_topics,
                "fill_queue": False,
            },
        )
        assert response.status_code == 201

    async def test_get_subscription(self, client: httpx.AsyncClient):
        realms_topics = ["foo:bar"]

        response = await client.get(f"{api_prefix}/subscription/{SUBSCRIBER_NAME}")
        assert response.status_code == 200
        data = response.json()

        assert data["name"] == SUBSCRIBER_NAME
        assert data["fill_queue"]
        assert data["fill_queue_status"] == FillQueueStatus.done
        assert len(data["realms_topics"]) == len(realms_topics)
        assert all(
            (realm_topic in data["realms_topics"] for realm_topic in realms_topics)
        )

    async def test_delete_subscription(self, client: httpx.AsyncClient):
        response = await client.delete(
            f"{api_prefix}/subscription/{SUBSCRIBER_NAME}?realm=foo&topic=bar",
        )
        assert response.status_code == 200
