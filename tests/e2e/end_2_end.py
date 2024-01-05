import asyncio

import pytest
import requests
import uuid

from ldap3.core.exceptions import LDAPBindError

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


def connect_ldap_server():
    try:
        server = ldap3.Server(settings.ldap_server_uri)
        connection = ldap3.Connection(
            server, settings.ldap_host_dn, settings.ldap_password
        )
        connection.bind()
    except LDAPBindError as e:
        connection = e
    return connection


def modify_obj(dn: str, changes: dict):
    ldap_server = connect_ldap_server()
    ldap_server.modify(dn, changes)


def delete_obj(dn: str):
    ldap_server = connect_ldap_server()
    ldap_server.delete(dn)


def add_obj(user_dn: str):
    ldap_conn = connect_ldap_server()
    response = ldap_conn.add(
        dn=user_dn,
        object_class=("posixGroup", "univentionObject", "univentionGroup"),
        attributes={"univentionObjectType": "groups/group", "gidNumber": 1},
    )
    return response


async def test_workflow():
    name = str(uuid.uuid4())
    user_dn = "cn=test_user,cn=groups,dc=univention-organization,dc=intranet"
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

    add_obj(user_dn)
    modify_obj(user_dn, changes)
    delete_obj(user_dn)

    await asyncio.sleep(
        10
    )  # need time for Dispatcher to send message to the consumer queue

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
    assert data[0]["data"]["body"]["new"]["dn"] == user_dn

    # Check modifying object
    assert data[1]["data"]["body"]["old"]["dn"] == user_dn
    assert (
        data[1]["data"]["body"]["new"]["properties"]["description"] == new_description
    )

    # Check deleting object
    assert data[2]["data"]["body"]["new"] is None
    assert data[2]["data"]["body"]["old"]["dn"] == user_dn


if __name__ == "__main__":
    asyncio.run(test_workflow())
