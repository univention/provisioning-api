import httpx
import pytest

from events.api import v1_prefix as events_api_prefix
from consumer.main import app as events_app


REALM = "foo"
TOPIC = "bar/baz"
BODY = {"hello": "world"}


@pytest.fixture(scope="function")
async def events_client():
    async with httpx.AsyncClient(
        app=events_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.anyio
class TestEvents:
    @pytest.mark.xfail(reason="MQ Adapter and dependency injection needed first")
    async def test_post_message(self, events_client: httpx.AsyncClient):
        response = await events_client.post(
            f"{events_api_prefix}/events/",
            json={
                "realm": REALM,
                "topic": TOPIC,
                "body": BODY,
            },
        )
        assert response.status_code == 202
