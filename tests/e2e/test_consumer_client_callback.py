# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import shared.client
from shared.models.queue import Message

from tests.e2e.helpers import create_message_via_events_api


async def test_no_callback_function_provided(
    provisioning_client: shared.client.AsyncClient, simple_subscription: str
):
    await provisioning_client.on_message(simple_subscription, message_limit=1)


async def test_get_one_message(
    provisioning_client: shared.client.AsyncClient,
    simple_subscription: str,
    provisioning_base_url,
):
    create_message_via_events_api(provisioning_base_url)

    result = []

    async def test_callback(message: Message):
        result.append(message)

    await provisioning_client.on_message(
        name=simple_subscription, callbacks=[test_callback], message_limit=1
    )

    assert len(result) == 1
