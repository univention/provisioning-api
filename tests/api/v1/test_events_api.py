import httpx
import pytest

from events.api import v1_prefix as api_prefix
from consumer.main import app


REALM = "foo"
TOPIC = "bar/baz"
BODY = {"hello": "world"}


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
class TestEvents:
    async def test_add_event(self, client: httpx.AsyncClient):
        response = await client.post(
            f"{api_prefix}/events/",
            json={
                "realm": REALM,
                "topic": TOPIC,
                "body": BODY,
            },
        )
        assert response.status_code == 202
