import uuid

from fastapi.testclient import TestClient

from dispatcher.api import v1_prefix as api_prefix
from dispatcher.main import app


def test_websocket():
    client = TestClient(app)
    name = str(uuid.uuid4())
    realm = "foo"
    topic = "bar/baz"
    body1 = {"first": {"foo": "1"}}
    body2 = {"second": {"bar": "2"}}

    response = client.post(
        f"{api_prefix}/subscription/",
        json={
            "name": name,
            "realms_topics": [[realm, topic]],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    response = client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body1,
        },
    )
    assert response.status_code == 202

    response = client.post(
        f"{api_prefix}/message/",
        json={
            "realm": realm,
            "topic": topic,
            "body": body2,
        },
    )
    assert response.status_code == 202

    with client.websocket_connect(f"{api_prefix}/subscription/{name}/ws") as ws_client:
        data = ws_client.receive_json()
        assert data["realm"] == realm
        assert data["topic"] == topic
        assert data["body"] == body1

        ws_client.send_json({"status": "ok"})

        data = ws_client.receive_json()
        assert data["realm"] == realm
        assert data["topic"] == topic
        assert data["body"] == body2
