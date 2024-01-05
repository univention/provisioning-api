import asyncio

import pytest
import requests
import uuid

from shared.config import settings
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.messages.api import v1_prefix as messages_api_prefix
import ldap3

REALM = "udm"
TOPIC = "groups/group"
PUBLISHER_NAME = "udm-listener"
BASE_URL = "http://localhost:7777"


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


def modify_obj(dn: str, changes: dict):
    server = ldap3.Server(settings.ldap_server_uri)
    with ldap3.Connection(
        server, settings.ldap_host_dn, settings.ldap_password
    ) as conn:
        conn.modify(dn, changes)


async def test_workflow():
    name = str(uuid.uuid4())
    obj_dn = "cn=Domain Guests,cn=groups,dc=univention-organization,dc=intranet"
    new_description = f"Description was changed by {name}"
    changes = {"description": [(ldap3.MODIFY_REPLACE, [new_description])]}

    # call of Consumer: create subscription

    response = requests.post(
        f"{BASE_URL}{subscriptions_api_prefix}/subscription",
        json={
            "name": name,
            "realm_topic": [REALM, TOPIC],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    # Trigger LDAP
    modify_obj(obj_dn, changes)

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
    assert data[0]["data"]["body"]["new"]["dn"] == obj_dn
    assert (
        data[0]["data"]["body"]["new"]["properties"]["description"] == new_description
    )
    assert data[0]["data"]["publisher_name"] == PUBLISHER_NAME


if __name__ == "__main__":
    asyncio.run(test_workflow())
