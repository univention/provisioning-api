# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import requests

from univention.admin.rest.client import UDM
from univention.provisioning.consumer import ProvisioningConsumerClient
from univention.provisioning.models import (
    MessageProcessingStatus,
    MessageProcessingStatusReport,
    PublisherName,
)
from univention.provisioning.models.queue import Body

from tests.conftest import DUMMY_TOPIC, REALM, TOPIC
from tests.e2e.conftest import E2ETestSettings


def create_message_via_events_api(test_settings: E2ETestSettings) -> Body:
    body = {"old": {}, "new": {str(uuid.uuid1()): str(uuid.uuid1())}}
    payload = {
        "publisher_name": PublisherName.consumer_client_test,
        "ts": "2024-02-07T09:01:33.835Z",
        "realm": REALM,
        "topic": DUMMY_TOPIC,
        "body": body,
    }
    response = requests.post(
        f"{test_settings.provisioning_api_base_url}/internal/v1/events",
        json=payload,
        auth=(
            test_settings.provisioning_events_username,
            test_settings.provisioning_events_password,
        ),
    )

    print(response.json())
    assert response.status_code == 202, "Failed to post message to queue"

    return Body.model_validate(body)


def create_message_via_udm_rest_api(udm: UDM):
    groups = udm.get(TOPIC)
    assert groups
    group = groups.new()
    group.properties["name"] = str(uuid.uuid1())
    group.save()

    return group


async def pop_all_messages(
    provisioning_client: ProvisioningConsumerClient,
    subscription_name: str,
    loop_number: int,
):
    result = []
    for _ in range(loop_number):
        message = await provisioning_client.get_subscription_message(
            name=subscription_name,
            timeout=1,
        )
        if message is None:
            continue
        report = MessageProcessingStatusReport(
            status=MessageProcessingStatus.ok,
            message_seq_num=message.sequence_number,
        )
        await provisioning_client.set_message_status(subscription_name, report)
        result.append(message)

    return result
