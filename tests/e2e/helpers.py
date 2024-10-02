# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid
from typing import Optional

import requests

from univention.admin.rest.client import UDM
from univention.provisioning.consumer import ProvisioningConsumerClient
from univention.provisioning.models import (
    MessageProcessingStatus,
    PublisherName,
)
from univention.provisioning.models.message import Body

from ..mock_data import DUMMY_TOPIC, REALM, USERS_TOPIC
from .conftest import E2ETestSettings


def create_message_via_events_api(test_settings: E2ETestSettings) -> Body:
    body = {"old": {}, "new": {str(uuid.uuid1()): str(uuid.uuid1()), "dn": "cn=foo,dc=bar"}}
    payload = {
        "publisher_name": PublisherName.consumer_client_test,
        "ts": "2024-02-07T09:01:33.835Z",
        "realm": REALM,
        "topic": DUMMY_TOPIC,
        "body": body,
    }
    response = requests.post(
        test_settings.messages_url,
        json=payload,
        auth=(test_settings.provisioning_events_username, test_settings.provisioning_events_password),
    )

    print(response.json())
    assert response.status_code == 202, "Failed to post message to queue"

    return Body.model_validate(body)


def create_udm_obj(udm: UDM, object_type: str, properties: dict, position: Optional[str] = None):
    objs = udm.get(object_type)
    assert objs
    obj = objs.new(position=position)
    obj.properties.update(properties)
    obj.save()
    return obj


def create_user_via_udm_rest_api(udm: UDM, extended_attributes: Optional[dict] = None):
    base_properties = {
        "username": str(uuid.uuid1()),
        "firstname": "John",
        "lastname": "Doe",
        "password": "password",
        "pwdChangeNextLogin": True,
    }
    properties = {**base_properties, **(extended_attributes or {})}
    return create_udm_obj(udm, USERS_TOPIC, properties)


def create_extended_attribute_via_udm_rest_api(udm: UDM):
    properties = {
        "name": "UniventionPasswordSelfServiceEmail",
        "CLIName": "PasswordRecoveryEmail",
        "module": ["users/user"],
        "syntax": "emailAddress",
        "default": "",
        "ldapMapping": "univentionPasswordSelfServiceEmail",
        "objectClass": "univentionPasswordSelfService",
        "shortDescription": "Password recovery e-mail address",
        "tabAdvanced": False,
        "tabName": "Password recovery",
        "multivalue": False,
        "valueRequired": False,
        "mayChange": True,
        "doNotSearch": False,
        "deleteObjectClass": False,
        "overwriteTab": False,
        "fullWidth": True,
    }
    position = f"cn=custom attributes,cn=univention,{udm.get_ldap_base()}"
    return create_udm_obj(udm, "settings/extended_attribute", properties, position)


async def pop_all_messages(
    provisioning_client: ProvisioningConsumerClient,
    subscription_name: str,
    loop_number: int,
):
    result = []
    for _ in range(loop_number):
        message = await provisioning_client.get_subscription_message(name=subscription_name, timeout=1)
        if message is None:
            continue
        await provisioning_client.set_message_status(
            subscription_name, message.sequence_number, MessageProcessingStatus.ok
        )
        result.append(message)

    return result
