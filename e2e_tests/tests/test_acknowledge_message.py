# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

from univention.provisioning.consumer.api import ProvisioningConsumerClient
from univention.provisioning.models.message import MessageProcessingStatus


async def test_get_multiple_messages(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    for i in range(2):
        # Start subscription in background BEFORE creating message.
        # This will ensure that the subscription is ready to receive messages.
        # Otherwise the subscription may be ready after the message has been
        # processed and removed from the queue.
        message_task = asyncio.create_task(
            provisioning_client.get_subscription_message(name=dummy_subscription, timeout=35)
        )

        # Small delay to ensure subscription is listening
        await asyncio.sleep(0.1)

        # Now create the message
        expected_body = create_message_via_events_api(test_settings)

        # Wait for the message to arrive
        message = await message_task
        assert message.body == expected_body
        await provisioning_client.set_message_status(
            dummy_subscription, message.sequence_number, MessageProcessingStatus.ok
        )


async def test_acknowledge_messages(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    # Start subscription in background BEFORE creating message.
    # This will ensure that the subscription is ready to receive messages.
    # Otherwise the subscription may be ready after the message has been
    # processed and removed from the queue.
    message_task = asyncio.create_task(
        provisioning_client.get_subscription_message(name=dummy_subscription, timeout=35)
    )

    # Small delay to ensure subscription is listening
    await asyncio.sleep(0.1)

    # Now create the message
    body = create_message_via_events_api(test_settings)

    # Wait for the message to arrive
    message = await message_task
    assert message.body == body

    await provisioning_client.set_message_status(
        dummy_subscription, message.sequence_number, MessageProcessingStatus.ok
    )


async def test_do_not_acknowledge_message(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    # Start subscription in background BEFORE creating any messages.
    # This will ensure that the subscription is ready to receive messages.
    # Otherwise the subscription may be ready after the message has been
    # processed and removed from the queue.
    message_task = asyncio.create_task(
        provisioning_client.get_subscription_message(name=dummy_subscription, timeout=35)
    )

    # Small delay to ensure subscription is listening
    await asyncio.sleep(0.1)

    # Now create the messages
    body1 = create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)

    # Get the first message (but don't acknowledge it)
    message1 = await message_task
    assert message1.body == body1

    # Try to get next message - should get no message since the first one is not acknowledged
    # and will be resent after a timeout of 30 seconds by the NATS server
    message2 = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=5)
    assert message2 is None

    # After some time, the first unacknowledged message should be redelivered
    # (This depends on NATS configuration for redelivery timeout)
    redelivered_message = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=35)
    assert redelivered_message is not None
    assert redelivered_message.body == body1  # Same as first message
    assert redelivered_message.sequence_number == message1.sequence_number  # Same sequence number
