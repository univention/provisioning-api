# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import aiohttp
import pytest
from univention.admin.rest.client import UDM
from univention.provisioning.consumer import AsyncClient

from tests.e2e.conftest import E2ETestSettings
from tests.e2e.helpers import (
    create_message_via_events_api,
    create_message_via_udm_rest_api,
    pop_all_messages,
)


async def test_create_subscription(provisioning_client: AsyncClient, simple_subscription):
    response = await provisioning_client.get_subscription(simple_subscription)
    assert response


async def test_get_empty_messages(provisioning_client: AsyncClient, simple_subscription: str):
    response = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=1,
    )

    assert response is None


async def test_send_message(
    provisioning_client: AsyncClient,
    simple_subscription: str,
    test_settings: E2ETestSettings,
):
    data = create_message_via_events_api(test_settings)

    response = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=10,
    )

    assert response.body == data


@pytest.mark.xfail()
async def test_pop_message(provisioning_client: AsyncClient, simple_subscription: str):
    response = await provisioning_client.get_subscription_message(name=simple_subscription, timeout=1, pop=True)

    assert response is None


async def test_get_real_messages(provisioning_client: AsyncClient, simple_subscription: str, udm: UDM):
    group = create_message_via_udm_rest_api(udm)  # noqa: F841

    response = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=5,
    )

    assert response is not None


async def test_get_multiple_messages(provisioning_client: AsyncClient, simple_subscription: str, udm: UDM):
    group1 = create_message_via_udm_rest_api(udm)  # noqa: F841
    group2 = create_message_via_udm_rest_api(udm)  # noqa: F841
    group3 = create_message_via_udm_rest_api(udm)  # noqa: F841

    result = await pop_all_messages(provisioning_client, simple_subscription, 6)
    assert len(result) == 3


@pytest.mark.xfail()
async def test_get_messages_zero_timeout(provisioning_client: AsyncClient, simple_subscription: str):
    response = await provisioning_client.get_subscription_message(
        name=simple_subscription,
        timeout=0,
    )

    assert response is None


async def test_get_messages_from_the_wrong_queue(provisioning_client: AsyncClient, simple_subscription: str):
    with pytest.raises(aiohttp.ClientResponseError, match="Unauthorized"):
        await provisioning_client.get_subscription_message(
            name="wrong_subscription_name",
            timeout=5,
        )
