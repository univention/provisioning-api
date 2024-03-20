# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import pytest

import shared.client
import shared.models.queue
from shared.models.api import MessageProcessingStatus, MessageProcessingStatusReport
from tests.e2e.helpers import create_message_via_events_api, pop_all_messages


async def test_get_multiple_messages(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    test_settings,
):
    create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)

    result = []

    for _ in range(3):
        response = await provisioning_client.get_subscription_messages(
            name=simple_subscription,
            timeout=8,
            count=1,
        )
        result.append(response)

    assert len(result) == 3


async def test_acknowledge_messages(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)

    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=5,
    )

    assert response[0].body == body
    message = response[0]

    report = MessageProcessingStatusReport(
        status=MessageProcessingStatus.ok,
        message_seq_num=message.sequence_number,
        publisher_name=message.publisher_name,
    )
    response = await provisioning_client.set_message_status(
        simple_subscription, [report]
    )

    response2 = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=1,
    )

    # Sometimes other messages like the "DC Backup Hosts" group can sneak into the queue
    # The test is considered successful if the response is empty or if the response is not a redelivery
    # of the previous message
    if response2:
        assert response2[0].body != body


@pytest.mark.xfail()
async def test_do_not_acknowledge_messages(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)

    # test first delivery of a message
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription, timeout=5, count=10
    )
    assert len(response) == 1
    assert response[0].data["body"] == body

    # test eventual redelivery of a message
    result = await pop_all_messages(provisioning_client, simple_subscription, 4)
    assert len(result) == 1
    assert result[0].body == body


@pytest.mark.xfail()
async def test_acknowledge_some_messages(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)

    # test first delivery of a message
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription, timeout=5, count=10
    )

    assert len(response) == 2
    assert response[0].data["body"] == body

    # test immediate redelivery of a message
    response = await provisioning_client.get_subscription_messages(
        name=simple_subscription,
        timeout=5,
        count=10,
    )
    assert response[0].data["body"] == body
    assert len(response) == 2

    # test redelivery only until message is acknowledged
    result = await pop_all_messages(provisioning_client, simple_subscription, 3)
    assert len(result) == 2

    create_message_via_events_api(test_settings)

    # test that only the new message gets delivered
    result = await pop_all_messages(provisioning_client, simple_subscription, 2)
    assert len(result) == 1
