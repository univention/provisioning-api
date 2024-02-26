# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import requests

import shared.client

from shared.models import PublisherName
from shared.models.api import MessageProcessingStatus, MessageProcessingStatusReport
from univention.admin.rest.client import UDM
from tests.conftest import REALM, TOPIC


def create_message_via_events_api(provisioning_base_url: str):
    body = {str(uuid.uuid1()): str(uuid.uuid1())}
    payload = {
        "publisher_name": PublisherName.consumer_client_test,
        "ts": "2024-02-07T09:01:33.835Z",
        "realm": REALM,
        "topic": TOPIC,
        "body": body,
    }

    response = requests.post(f"{provisioning_base_url}/events/v1/events", json=payload)

    print(response.json())
    assert response.status_code == 202, "Failed to post message to queue"

    return body


def create_message_via_udm_rest_api(udm: UDM):
    groups = udm.get(TOPIC)
    assert groups
    group = groups.new()
    group.properties["name"] = str(uuid.uuid1())
    group.save()

    return group


async def pop_all_messages(
    provisioning_client: shared.client.AsyncClient,
    subscription_name: str,
    loop_number: int,
):
    result = []
    for _ in range(loop_number):
        response = await provisioning_client.get_subscription_messages(
            name=subscription_name,
            timeout=1,
            count=1,
        )
        if not response:
            continue
        report = MessageProcessingStatusReport(
            status=MessageProcessingStatus.ok,
            message_seq_num=response[0].sequence_number,
            publisher_name=response[0].publisher_name,
        )
        await provisioning_client.set_message_status(subscription_name, [report])
        result.append(response[0])

    return result
