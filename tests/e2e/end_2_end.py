import asyncio
from time import sleep

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


def trigger_ldap(dn: str, changes: dict):
    server = ldap3.Server(settings.ldap_server_uri)
    with ldap3.Connection(
        server, settings.ldap_host_dn, settings.ldap_password
    ) as conn:
        conn.add(
            dn=dn,
            object_class=("posixGroup", "univentionObject", "univentionGroup"),
            attributes={"univentionObjectType": "groups/group", "gidNumber": 1},
        )
        conn.modify(dn, changes)
        sleep(1)  # needs time to apply changes
        conn.delete(dn)


async def test_workflow():
    name = str(uuid.uuid4())
    dn = "cn=test_user,cn=groups,dc=univention-organization,dc=intranet"
    new_description = "New description"
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

    trigger_ldap(dn, changes)

    # needs time for Dispatcher to send message to the consumer queue
    await asyncio.sleep(10)

    response = requests.get(
        f"{BASE_URL}{messages_api_prefix}/subscription/{name}/message?count=3"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3

    for i in range(3):
        assert data[i]["data"]["realm"] == REALM
        assert data[i]["data"]["topic"] == TOPIC
        assert data[i]["data"]["publisher_name"] == PUBLISHER_NAME

    # Check creating object
    assert data[0]["data"]["body"]["old"] is None
    assert data[0]["data"]["body"]["new"]["dn"] == dn

    # Check modifying object
    assert data[1]["data"]["body"]["old"]["dn"] == dn
    assert (
        data[1]["data"]["body"]["new"]["properties"]["description"] == new_description
    )

    # Check deleting object
    assert data[2]["data"]["body"]["new"] is None
    assert data[2]["data"]["body"]["old"]["dn"] == dn


if __name__ == "__main__":
    asyncio.run(test_workflow())
