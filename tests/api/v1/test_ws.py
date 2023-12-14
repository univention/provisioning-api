import pytest
from fastapi.testclient import TestClient
from tests.conftest import SUBSCRIBER_NAME
from consumer.messages.api import v1_prefix as messages_api_prefix
from events.api import v1_prefix as events_api_prefix
from consumer.main import app

REALM = "udm"
TOPIC = "users/user"
BODY = {"user": "new_user_object"}


@pytest.mark.anyio
def test_websocket(override_dependencies_events):
    client = TestClient(app)

    response = client.post(
        f"{events_api_prefix}/events/",
        json={
            "realm": REALM,
            "topic": TOPIC,
            "body": BODY,
        },
    )
    assert response.status_code == 202

    with client.websocket_connect(
        f"{messages_api_prefix}/subscription/{SUBSCRIBER_NAME}/ws"
    ) as ws_client:
        data = ws_client.receive_json()

        assert data["realm"] == REALM
        assert data["topic"] == TOPIC
        assert data["body"] == BODY
