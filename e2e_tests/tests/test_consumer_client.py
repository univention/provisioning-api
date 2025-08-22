# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import uuid

import aiohttp
import pytest

from univention.admin.rest.client import UDM, UnprocessableEntity
from univention.provisioning.consumer.api import ProvisioningConsumerClient
from univention.provisioning.models.message import MessageProcessingStatus

from .e2e_settings import E2ETestSettings


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


async def test_create_subscription(provisioning_client: ProvisioningConsumerClient, dummy_subscription):
    response = await provisioning_client.get_subscription(dummy_subscription)
    assert response


async def test_get_empty_messages(provisioning_client: ProvisioningConsumerClient, dummy_subscription: str):
    response = await provisioning_client.get_subscription_message(
        name=dummy_subscription,
        timeout=1,
    )

    assert response is None


async def test_send_message(
    create_message_via_events_api,
    provisioning_client: ProvisioningConsumerClient,
    dummy_subscription: str,
    test_settings: E2ETestSettings,
):
    # Start subscription in background BEFORE creating message.
    # This will ensure that the subscription is ready to receive messages.
    # Otherwise the subscription may be ready after the message has been
    # processed and removed from the queue.
    message_task = asyncio.create_task(
        provisioning_client.get_subscription_message(name=dummy_subscription, timeout=10)
    )

    # Small delay to ensure subscription is listening
    await asyncio.sleep(0.1)

    # Now create the message
    data = create_message_via_events_api(test_settings)

    # Wait for the message
    response = await message_task
    assert response.body == data


@pytest.mark.xfail()
async def test_pop_message(provisioning_client: ProvisioningConsumerClient, dummy_subscription: str):
    response = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=1, pop=True)

    assert response is None


async def test_get_real_messages(
    create_user_via_udm_rest_api, provisioning_client: ProvisioningConsumerClient, real_subscription: str, udm: UDM
):
    # Start subscription in background BEFORE creating user.
    # This will ensure that the subscription is ready to receive messages.
    # Otherwise the subscription may be ready after the message has been
    # processed and removed from the queue.
    message_task = asyncio.create_task(provisioning_client.get_subscription_message(name=real_subscription, timeout=15))

    # Small delay to ensure subscription is listening
    await asyncio.sleep(0.1)

    # Now create the user
    user = create_user_via_udm_rest_api()  # noqa: F841

    # Wait for the message
    response = await message_task
    assert response is not None
    assert response.body.new["properties"]["univentionObjectIdentifier"]
    uuid.UUID(response.body.new["properties"]["univentionObjectIdentifier"])


async def test_get_multiple_messages(
    create_user_via_udm_rest_api, provisioning_client: ProvisioningConsumerClient, real_subscription: str, udm: UDM
):
    users = []
    for i in range(3):
        # Start subscription in background BEFORE creating user.
        # This will ensure that the subscription is ready to receive messages.
        # Otherwise the subscription may be ready after the message has been
        # processed and removed from the queue.
        message_task = asyncio.create_task(
            provisioning_client.get_subscription_message(name=real_subscription, timeout=15)
        )

        # Small delay to ensure subscription is listening
        await asyncio.sleep(0.1)

        # Create user
        user = create_user_via_udm_rest_api()  # noqa: F841
        users.append(user)

        # Wait for message and acknowledge it
        message = await message_task
        assert message is not None
        await provisioning_client.set_message_status(
            real_subscription, message.sequence_number, MessageProcessingStatus.ok
        )


@pytest.mark.xfail()
async def test_get_messages_zero_timeout(provisioning_client: ProvisioningConsumerClient, dummy_subscription: str):
    response = await provisioning_client.get_subscription_message(
        name=dummy_subscription,
        timeout=0,
    )

    assert response is None


async def test_get_messages_from_the_wrong_queue(
    provisioning_client: ProvisioningConsumerClient, dummy_subscription: str
):
    with pytest.raises(aiohttp.ClientResponseError, match="Unauthorized"):
        await provisioning_client.get_subscription_message(
            name="wrong_subscription_name",
            timeout=5,
        )


async def test_create_user_with_extended_attribute(
    create_extended_attribute,
    create_user_via_udm_rest_api,
    provisioning_client: ProvisioningConsumerClient,
    real_subscription: str,
):
    # Start subscription in background BEFORE creating user.
    # This will ensure that the subscription is ready to receive messages.
    # This will ensure that the subscription is ready to receive messages.
    # Otherwise the subscription may be ready after the message has been
    # processed and removed from the queue.
    message_task = asyncio.create_task(provisioning_client.get_subscription_message(name=real_subscription, timeout=5))

    # Small delay to ensure subscription is listening
    await asyncio.sleep(0.1)

    # Now create the user
    user = create_user_via_udm_rest_api({"PasswordRecoveryEmail": "test@univention.de"})

    # Wait for the message
    message = await message_task
    assert message.body.new.get("dn") == user.dn
    assert message.body.new["properties"]["PasswordRecoveryEmail"] == user.properties["PasswordRecoveryEmail"]


async def test_create_user_with_missing_extended_attribute(
    create_user_via_udm_rest_api, provisioning_client: ProvisioningConsumerClient, real_subscription: str
):
    with pytest.raises(UnprocessableEntity, match="The User module has no property PasswordRecoveryEmail."):
        create_user_via_udm_rest_api({"PasswordRecoveryEmail": "test@univention.de"})
