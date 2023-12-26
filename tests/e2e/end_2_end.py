import asyncio

import requests
import uuid

from tests.conftest import REALM_TOPIC, TOPIC, BODY, PUBLISHER_NAME, REALM
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.messages.api import v1_prefix as messages_api_prefix

from udm_messaging.port import UDMMessagingPort
from udm_messaging.service.udm import UDMMessagingService

BASE_URL = "http://localhost:7777"


async def test_workflow():
    name = str(uuid.uuid4())
    # call of Consumer: create subscription

    response = requests.post(
        f"{BASE_URL}{subscriptions_api_prefix}/subscription",
        json={
            "name": name,
            "realm_topic": REALM_TOPIC,
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    # Skip triggering LDAP

    # call of UDMMessagingService: send event to Event REST API

    async with UDMMessagingPort.port_context() as port:
        service = UDMMessagingService(port)
        await service.send_event({"New": "Object"}, {"Old": "Object"})

    await asyncio.sleep(
        5
    )  # need time for Dispatcher to send message to the consumer queue

    # call of Consumer: get messages from consumer queue

    response = requests.get(
        f"{BASE_URL}{messages_api_prefix}/subscription/{name}/message"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["data"]["realm"] == REALM
    assert data[0]["data"]["topic"] == TOPIC
    assert data[0]["data"]["body"] == BODY
    assert data[0]["data"]["publisher_name"] == PUBLISHER_NAME


if __name__ == "__main__":
    asyncio.run(test_workflow())
