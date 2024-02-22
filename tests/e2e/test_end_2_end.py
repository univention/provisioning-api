# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import pytest
import requests
import uuid

from shared.config import settings
from consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix
from consumer.messages.api import v1_prefix as messages_api_prefix
import ldap3

from shared.models import PublisherName

REALM = "udm"
TOPIC = "groups/group"
PUBLISHER_NAME = PublisherName.udm_listener


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


def connect_ldap_server():
    server = ldap3.Server(settings.ldap_server_uri)
    connection = ldap3.Connection(server, settings.ldap_host_dn, settings.ldap_password)
    connection.bind()
    return connection


async def test_workflow(provisioning_base_url):
    name = str(uuid.uuid4())
    dn = "cn=test_user,cn=groups,dc=univention-organization,dc=intranet"
    new_description = "New description"
    changes = {"description": [(ldap3.MODIFY_REPLACE, [new_description])]}
    connection = connect_ldap_server()

    response = requests.post(
        f"{provisioning_base_url}{subscriptions_api_prefix}/subscriptions",
        json={
            "name": name,
            "realms_topics": [[REALM, TOPIC]],
            "request_prefill": False,
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
        f"{provisioning_base_url}{messages_api_prefix}/subscriptions/{name}/messages?count=5&pop=true"
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PUBLISHER_NAME
    assert message["body"]["old"] is None
    assert message["body"]["new"]["dn"] == dn

    # Test modifying object
    connection.modify(dn, changes)

    response = requests.get(
        f"{provisioning_base_url}{messages_api_prefix}/subscriptions/{name}/messages?count=5&pop=true"
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PUBLISHER_NAME
    assert message["body"]["old"]["dn"] == dn
    assert message["body"]["new"]["properties"]["description"] == new_description

    # Test deleting object
    connection.delete(dn)

    response = requests.get(
        f"{provisioning_base_url}{messages_api_prefix}/subscriptions/{name}/messages?count=5&pop=true"
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PUBLISHER_NAME
    assert message["body"]["new"] is None
    assert message["body"]["old"]["dn"] == dn
