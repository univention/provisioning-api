from fastapi.testclient import TestClient
import httpx
import pytest
import uuid

from events.api import v1_prefix as events_api_prefix
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.messages.api import v1_prefix as messages_api_prefix
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
@pytest.mark.xfail(reason="to make this work, a real MQ backend needs to be working")
async def test_udm_create_user_event_is_routed_correctly(
    producer: httpx.AsyncClient,
    consumer: httpx.AsyncClient,
    override_dependencies,
    override_dependencies_events,
):
    # register a consumer
    name = str(uuid.uuid4())
    realms_topics = [
        [REALM, TOPIC],
    ]

    response = await consumer.post(
        f"{subscriptions_api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": realms_topics,
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    # call event api with new user event
    response = await producer.post(
        f"{events_api_prefix}/events/",
        json={
            "realm": REALM,
            "topic": TOPIC,
            "body": BODY,
        },
    )
    assert response.status_code == 202

    message_consumer = TestClient(app)
    # evaluate that the message about a new user is received by the consumer
    with message_consumer.websocket_connect(
        f"{messages_api_prefix}/subscription/{name}/ws"
    ) as ws_client:
        data = ws_client.receive_json()

        assert data["realm"] == REALM
        assert data["topic"] == TOPIC
        assert data["body"] == BODY
