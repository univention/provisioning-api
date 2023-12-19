import httpx
import pytest
from tests.conftest import FLAT_MESSAGE

from events.api import v1_prefix as events_api_prefix
from consumer.main import app


@pytest.fixture(scope="session")
async def client():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
class TestEvents:
    async def test_add_event(
        self, client: httpx.AsyncClient, override_dependencies_events
    ):
        response = await client.post(f"{events_api_prefix}/events/", json=FLAT_MESSAGE)
        assert response.status_code == 202
