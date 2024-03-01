# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import pytest

import shared.client
from shared.models.queue import Message

from tests.e2e.helpers import create_message_via_events_api


async def test_no_callback_function_provided(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    with pytest.raises(ValueError):
        await shared.client.MessageHandler(
            provisioning_client, simple_subscription, [], message_limit=1
        ).run()


async def test_get_one_message(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    provisioning_base_url,
):
    create_message_via_events_api(provisioning_base_url)

    result = []

    async def test_callback(message: Message):
        result.append(message)

    await shared.client.MessageHandler(
        provisioning_client, simple_subscription, [test_callback], message_limit=1
    ).run()

    assert len(result) == 1


async def test_timeout_while_waiting_for_messages(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    provisioning_base_url,
):
    create_message_via_events_api(provisioning_base_url)

    response = await provisioning_client.get_subscription_messages(
        simple_subscription,
        timeout=10,
    )

    assert len(response) == 1


async def test_get_multiple_messages(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    provisioning_base_url,
):
    create_message_via_events_api(provisioning_base_url)
    create_message_via_events_api(provisioning_base_url)
    create_message_via_events_api(provisioning_base_url)

    result = []

    async def test_callback(message: Message):
        result.append(message)

    await shared.client.MessageHandler(
        provisioning_client, simple_subscription, [test_callback], message_limit=3
    ).run()

    assert len(result) == 3
