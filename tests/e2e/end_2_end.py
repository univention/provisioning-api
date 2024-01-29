# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

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


def connect_ldap_server():
    server = ldap3.Server(settings.ldap_server_uri)
    connection = ldap3.Connection(server, settings.ldap_host_dn, settings.ldap_password)
    connection.bind()
    return connection


async def test_workflow():
    name = str(uuid.uuid4())
    dn = "cn=test_user,cn=groups,dc=univention-organization,dc=intranet"
    new_description = "New description"
    changes = {"description": [(ldap3.MODIFY_REPLACE, [new_description])]}
    connection = connect_ldap_server()

    response = requests.post(
        f"{BASE_URL}{subscriptions_api_prefix}/subscriptions",
        json={
            "name": name,
            "realm_topic": [REALM, TOPIC],
            "fill_queue": False,
        },
    )
    assert response.status_code == 201

    # Test creating object
    connection.add(
        dn=dn,
        object_class=("posixGroup", "univentionObject", "univentionGroup"),
        attributes={"univentionObjectType": "groups/group", "gidNumber": 1},
    )

    response = requests.get(
        f"{BASE_URL}{messages_api_prefix}/subscription/{name}/message?count=5&pop=true"
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]["data"]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PUBLISHER_NAME
    assert message["body"]["old"] is None
    assert message["body"]["new"]["dn"] == dn

    # Test modifying object
    connection.modify(dn, changes)

    response = requests.get(
        f"{BASE_URL}{messages_api_prefix}/subscription/{name}/message?count=5&pop=true"
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]["data"]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PUBLISHER_NAME
    assert message["body"]["old"]["dn"] == dn
    assert message["body"]["new"]["properties"]["description"] == new_description

    # Test deleting object
    connection.delete(dn)

    response = requests.get(
        f"{BASE_URL}{messages_api_prefix}/subscriptions/{name}/messages?count=5&pop=true"
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]["data"]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PUBLISHER_NAME
    assert message["body"]["new"] is None
    assert message["body"]["old"]["dn"] == dn


if __name__ == "__main__":
    asyncio.run(test_workflow())
