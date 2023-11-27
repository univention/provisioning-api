import httpx
import pytest

from events.api import v1_prefix as api_prefix
from consumer.main import app


REALM = "udm"
TOPIC = "users/user"
BODY = {"user": "new_user_object"}  # TODO: look this up!


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def producer():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.fixture(scope="session")
async def consumer():
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest.mark.anyio
async def test_udm_create_user_event_is_routed_correctly(
    producer: httpx.AsyncClient, consumer: httpx.AsyncClient
):
    # register a consumer
    # call event api with new user event
    # evaluate that the message about a new user is received by the consumer
    response = await producer.post(
        f"{api_prefix}/events/",
        json={
            "realm": REALM,
            "topic": TOPIC,
            "body": BODY,
        },
    )
    assert response.status_code == 202
