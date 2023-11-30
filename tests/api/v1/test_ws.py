import pytest
from fastapi.testclient import TestClient
from tests.conftest import NAME
from consumer.messages.api import v1_prefix as messages_api_prefix
from events.api import v1_prefix as events_api_prefix
from consumer.main import app


@pytest.mark.anyio
def test_websocket(override_dependencies_events):
    client = TestClient(app)
    realm = "foo"
    topic = "bar/baz"
    body = {"hello": "world"}

    response = client.post(
        f"{events_api_prefix}/events/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body,
        },
    )
    assert response.status_code == 202

    with client.websocket_connect(
        f"{messages_api_prefix}/subscription/{NAME}/ws"
    ) as ws_client:
        data = ws_client.receive_json()

        assert data["realm"] == realm
        assert data["topic"] == topic
        assert data["body"] == body
