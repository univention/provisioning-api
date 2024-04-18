# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from client import AsyncClient
from shared.models import MessageProcessingStatus, MessageProcessingStatusReport
from tests.e2e.helpers import create_message_via_events_api


async def test_get_multiple_messages(
    provisioning_client: AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body_1 = create_message_via_events_api(test_settings)
    body_2 = create_message_via_events_api(test_settings)

    for body in [body_1, body_2]:
        response = await provisioning_client.get_subscription_message(
            name=simple_subscription,
            timeout=5,
            count=1,
        )
        message = response[0]
        assert message.body == body
        report = MessageProcessingStatusReport(
            status=MessageProcessingStatus.ok,
            message_seq_num=message.sequence_number,
        )
        await provisioning_client.set_message_status(simple_subscription, [report])


async def test_acknowledge_messages(
    provisioning_client: AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)

    response = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=5,
    )

    message = response[0]
    assert message.body == body

    report = MessageProcessingStatusReport(
        status=MessageProcessingStatus.ok,
        message_seq_num=message.sequence_number,
    )
    await provisioning_client.set_message_status(simple_subscription, [report])

    response2 = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=35,
    )

    # Sometimes other messages like the "DC Backup Hosts" group can sneak into the queue
    # The test is considered successful if the response is empty or if the response is not a redelivery
    # of the previous message
    if response2:
        assert response2[0].body != body


async def test_do_not_acknowledge_message(
    provisioning_client: AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)

    # test first delivery of a message
    response = await provisioning_client.get_subscription_message(
        name=simple_subscription, timeout=5, count=1
    )
    assert len(response) == 1
    assert response[0].body == body

    # test that the same unacknowledged message is delivered
    response2 = await provisioning_client.get_subscription_message(
        name=simple_subscription, timeout=35, count=1
    )
    assert len(response2) == 1
    assert response2[0].body == body
