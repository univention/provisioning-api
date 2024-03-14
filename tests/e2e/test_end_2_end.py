# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

import pytest
import requests
import uuid
from app.main import internal_app_path
import ldap3

from app.admin.api import v1_prefix as admin_api_prefix
from app.consumer.messages.api import v1_prefix as messages_api_prefix
from app.consumer.subscriptions.api import v1_prefix as subscriptions_api_prefix

from shared.client.config import Settings

from shared.models import PublisherName

from shared.models import FillQueueStatus

REALM = "udm"
TOPIC = "groups/group"
PASSWORD = "password"


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
def ldap_connection(pytestconfig):
    server = ldap3.Server(pytestconfig.option.ldap_server_uri)
    connection = ldap3.Connection(
        server,
        pytestconfig.option.ldap_host_dn,
        pytestconfig.option.ldap_password,
    )
    connection.bind()
    return connection


async def test_workflow(
    provisioning_api_base_url, ldap_connection, admin_settings: Settings
):
    name = str(uuid.uuid4())
    # TODO: randomize the group name
    dn = "cn=test_user,cn=groups,dc=univention-organization,dc=intranet"
    new_description = "New description"
    changes = {"description": [(ldap3.MODIFY_REPLACE, [new_description])]}

    response = requests.post(
        f"{provisioning_api_base_url}{internal_app_path}{admin_api_prefix}/subscriptions",
        json={
            "name": name,
            "realms_topics": [[REALM, TOPIC]],
            "request_prefill": False,
            "password": PASSWORD,
        },
        auth=(
            admin_settings.provisioning_api_username,
            admin_settings.provisioning_api_password,
        ),
    )
    assert response.status_code == 201

    # Test creating object
    result = ldap_connection.add(
        dn=dn,
        object_class=("posixGroup", "univentionObject", "univentionGroup"),
        attributes={"univentionObjectType": "groups/group", "gidNumber": 1},
    )
    assert (
        result is True
    ), "No ldap change triggered, possibly due to test data colision"

    response = requests.get(
        f"{provisioning_api_base_url}{messages_api_prefix}/subscriptions/{name}/messages?count=5&pop=true",
        auth=(name, PASSWORD),
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PublisherName.udm_listener
    assert message["body"]["old"] is None
    assert message["body"]["new"]["dn"] == dn

    # Test modifying object
    ldap_connection.modify(dn, changes)

    response = requests.get(
        f"{provisioning_api_base_url}{messages_api_prefix}/subscriptions/{name}/messages?count=5&pop=true",
        auth=(name, PASSWORD),
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PublisherName.udm_listener
    assert message["body"]["old"]["dn"] == dn
    assert message["body"]["new"]["properties"]["description"] == new_description

    # Test deleting object
    ldap_connection.delete(dn)

    response = requests.get(
        f"{provisioning_api_base_url}{messages_api_prefix}/subscriptions/{name}/messages?count=5&pop=true",
        auth=(name, PASSWORD),
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PublisherName.udm_listener
    assert message["body"]["new"] is None
    assert message["body"]["old"]["dn"] == dn


async def test_prefill(admin_settings, provisioning_api_base_url):
    name = str(uuid.uuid4())

    response = requests.post(
        f"{provisioning_api_base_url}{internal_app_path}{admin_api_prefix}/subscriptions",
        json={
            "name": name,
            "realms_topics": [[REALM, TOPIC]],
            "request_prefill": True,
            "password": PASSWORD,
        },
        auth=(
            admin_settings.provisioning_api_username,
            admin_settings.provisioning_api_password,
        ),
    )
    assert response.status_code == 201

    # ensure that the pre-fill process is finished successfully
    while True:
        response = requests.get(
            f"{provisioning_api_base_url}{subscriptions_api_prefix}/subscriptions/{name}",
            auth=(name, PASSWORD),
        )
        assert response.status_code == 200
        prefill_queue_status = response.json()["prefill_queue_status"]
        if prefill_queue_status == FillQueueStatus.failed:
            assert False
        elif prefill_queue_status == FillQueueStatus.done:
            break
        await asyncio.sleep(1)

    response = requests.get(
        f"{provisioning_api_base_url}{messages_api_prefix}/subscriptions/{name}/messages?count=1&pop=true",
        auth=(name, PASSWORD),
    )
    assert response.status_code == 200

    data = response.json()
    message = data[0]

    assert len(data) == 1
    assert message["realm"] == REALM
    assert message["topic"] == TOPIC
    assert message["publisher_name"] == PublisherName.udm_pre_fill
