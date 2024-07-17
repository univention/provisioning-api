# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from univention.provisioning.consumer import AsyncClient
from univention.provisioning.models import (
    MessageProcessingStatus,
    MessageProcessingStatusReport,
)

from tests.e2e.helpers import create_message_via_events_api


async def test_get_multiple_messages(
    provisioning_client: AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body_1 = create_message_via_events_api(test_settings)
    body_2 = create_message_via_events_api(test_settings)

    for body in [body_1, body_2]:
        message = await provisioning_client.get_subscription_message(
            name=simple_subscription,
            timeout=5,
        )
        assert message.body == body
        report = MessageProcessingStatusReport(
            status=MessageProcessingStatus.ok,
            message_seq_num=message.sequence_number,
        )
        await provisioning_client.set_message_status(simple_subscription, report)


async def test_acknowledge_messages(
    provisioning_client: AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)

    message = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=5,
    )

    assert message.body == body

    report = MessageProcessingStatusReport(
        status=MessageProcessingStatus.ok,
        message_seq_num=message.sequence_number,
    )
    await provisioning_client.set_message_status(simple_subscription, report)

    response2 = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=35,
    )

    # Sometimes other messages like the "DC Backup Hosts" group can sneak into the queue
    # The test is considered successful if the response is empty or if the response is not a redelivery
    # of the previous message
    if response2:
        assert response2.body != body


async def test_do_not_acknowledge_message(
    provisioning_client: AsyncClient,
    simple_subscription: str,
    test_settings,
):
    body = create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)

    # test the first delivery of a message
    message = await provisioning_client.get_subscription_message(name=simple_subscription, timeout=5)
    assert message.body == body

    # test that the next message will not be delivered until the first one is temporary out of the stream
    message2 = await provisioning_client.get_subscription_message(name=simple_subscription, timeout=5)
    assert message2 is None

    # test that the same unacknowledged message is delivered after 30 seconds of unavailability
    message3 = await provisioning_client.get_subscription_message(name=simple_subscription, timeout=30)
    assert message3.body == body
