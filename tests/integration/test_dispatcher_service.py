from unittest.mock import AsyncMock

import httpx
import pytest
from tests.conftest import SUBSCRIBER_NAME
from consumer.main import app as messages_app
from consumer.messages.api import v1_prefix as messages_api_prefix

from tests.conftest import FakeKvStore, FakeJs, MSG
from dispatcher.port import DispatcherPort
from dispatcher.service.dispatcher import DispatcherService
from events.api import v1_prefix as events_api_prefix
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
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


@pytest.fixture
def port_with_mock_nats():
    port = DispatcherPort()
    port._nats_adapter.kv_store = FakeKvStore()
    port._nats_adapter.js = FakeJs()
    port._nats_adapter.nats = AsyncMock()
    port._nats_adapter._future = AsyncMock()
    port._nats_adapter.wait_for_event = AsyncMock(return_value=MSG)
    return port


@pytest.fixture(scope="session")
async def messages_client():
    async with httpx.AsyncClient(
        app=messages_app, base_url="http://testserver"
    ) as client:
        yield client


@pytest.mark.anyio
class TestDispatcher:
    async def test_store_event_in_the_consumer_queue(
        self,
        producer: httpx.AsyncClient,
        consumer: httpx.AsyncClient,
        messages_client: httpx.AsyncClient,
        port_with_mock_nats: DispatcherPort,
        override_dependencies_events,
    ):
        # register a consumer
        realm_topic = [REALM, TOPIC]

        response = await consumer.post(
            f"{subscriptions_api_prefix}/subscription/",
            json={
                "name": SUBSCRIBER_NAME,
                "realm_topic": realm_topic,
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

        # trigger dispatcher to retrieve event from incoming queue
        # TODO: create fake Nats for more realistic testing
        port_with_mock_nats._nats_adapter.add_message = AsyncMock(
            side_effect=Exception("Stop waiting for the new event")
        )
        service = DispatcherService(port_with_mock_nats)
        await service.store_event_in_consumer_queues()

        # check subscribing to the incoming queue
        port_with_mock_nats._nats_adapter.nats.subscribe.assert_called_once_with(
            "incoming", cb=port_with_mock_nats._nats_adapter.cb
        )
        # check waiting for event
        port_with_mock_nats._nats_adapter.wait_for_event.assert_called_once_with()
        # check storing event in the consumer queue
        port_with_mock_nats._nats_adapter.add_message.assert_called_once()

        # check whether the event was stored in the consumer queue
        response = await messages_client.get(
            f"{messages_api_prefix}/subscription/{SUBSCRIBER_NAME}/message"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["data"]["realm"] == REALM
        assert data[0]["data"]["topic"] == TOPIC
        assert data[0]["data"]["body"] == BODY
        assert data[0]["data"]["publisher_name"] == "127.0.0.1"
