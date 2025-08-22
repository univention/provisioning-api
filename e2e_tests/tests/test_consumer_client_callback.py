# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

import pytest

from univention.provisioning.consumer.api import MessageHandler, MessageHandlerSettings, ProvisioningConsumerClient
from univention.provisioning.models.message import Message


@pytest.fixture()
async def test_no_callback_function_provided(provisioning_client: ProvisioningConsumerClient, dummy_subscription: str):
    with pytest.raises(ValueError, match="Callback functions can't be empty"):
        await MessageHandler(
            client=provisioning_client,
            callbacks=[],
            settings=MessageHandlerSettings(max_acknowledgement_retries=5),
            message_limit=1,
        ).run()


@pytest.mark.timeout(10)
async def test_get_one_message(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    result = []

    async def test_callback(message: Message):
        result.append(message)

    # Start MessageHandler in background BEFORE creating message
    handler_task = asyncio.create_task(
        MessageHandler(
            client=provisioning_client,
            callbacks=[test_callback],
            settings=MessageHandlerSettings(max_acknowledgement_retries=5),
            message_limit=1,
        ).run()
    )

    # Small delay to ensure handler is listening
    await asyncio.sleep(0.1)

    # Now create the message
    create_message_via_events_api(test_settings)

    # Wait for handler to complete
    await handler_task

    assert len(result) == 1


async def test_timeout_while_waiting_for_messages(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    # Start subscription in background BEFORE creating message
    message_task = asyncio.create_task(provisioning_client.get_subscription_message(dummy_subscription, timeout=10))

    # Small delay to ensure subscription is listening
    await asyncio.sleep(0.1)

    # Now create the message
    body = create_message_via_events_api(test_settings)

    # Wait for the message
    response = await message_task
    assert response.body == body


@pytest.mark.timeout(10)
async def test_get_multiple_messages(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings,
):
    result = []

    async def test_callback(message: Message):
        result.append(message)

    # Start MessageHandler in background BEFORE creating messages
    handler_task = asyncio.create_task(
        MessageHandler(
            client=provisioning_client,
            callbacks=[test_callback],
            settings=MessageHandlerSettings(max_acknowledgement_retries=5),
            message_limit=3,
        ).run()
    )

    # Small delay to ensure handler is listening
    await asyncio.sleep(0.1)

    # Now create the messages
    create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)
    create_message_via_events_api(test_settings)

    # Wait for handler to complete
    await handler_task

    assert len(result) == 3

    assert len(result) == 3
