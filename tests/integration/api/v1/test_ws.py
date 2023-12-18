import uuid

import pytest
from fastapi.testclient import TestClient
from tests.conftest import REALM, TOPIC, BODY, FLAT_MESSAGE

from consumer.messages.api import v1_prefix as messages_api_prefix
from events.api import v1_prefix as events_api_prefix
from consumer.main import app


@pytest.mark.anyio
def test_websocket(override_dependencies_events):
    client = TestClient(app)
    name = str(uuid.uuid4())

    response = client.post(f"{events_api_prefix}/events/", json=FLAT_MESSAGE)
    assert response.status_code == 202

    with client.websocket_connect(
        f"{messages_api_prefix}/subscription/{name}/ws"
    ) as ws_client:
        data = ws_client.receive_json()

        assert data["realm"] == REALM
        assert data["topic"] == TOPIC
        assert data["body"] == BODY