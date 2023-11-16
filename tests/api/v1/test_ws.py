import uuid

import pytest
from fastapi.testclient import TestClient

from consumer.messages.api import v1_prefix as messages_api_prefix
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.main import app


# @pytest.mark.anyio
@pytest.mark.skip(reason="Need to fix it later")
def test_websocket():
    client = TestClient(app)
    name = str(uuid.uuid4())
    realm = "foo"
    topic = "bar/baz"
    body = {"hello": "world"}

    response = client.post(
        f"{subscriptions_api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": [[realm, topic]],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = client.post(
        f"{messages_api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body,
        },
    )
    assert response.status_code == 202

    with client.websocket_connect(
        f"{messages_api_prefix}/subscription/{name}/ws"
    ) as ws_client:
        data = ws_client.receive_json()

        assert data["realm"] == realm
        assert data["topic"] == topic
        assert data["body"] == body
