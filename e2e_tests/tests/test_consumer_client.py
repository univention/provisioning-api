# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

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
    data = create_message_via_events_api(test_settings)

    response = await provisioning_client.get_subscription_message(
        name=dummy_subscription,
        timeout=10,
    )

    assert response.body == data


@pytest.mark.xfail()
async def test_pop_message(provisioning_client: ProvisioningConsumerClient, dummy_subscription: str):
    response = await provisioning_client.get_subscription_message(name=dummy_subscription, timeout=1, pop=True)

    assert response is None


async def test_get_real_messages(
    create_user_via_udm_rest_api, provisioning_client: ProvisioningConsumerClient, real_subscription: str, udm: UDM
):
    user = create_user_via_udm_rest_api()  # noqa: F841

    response = await provisioning_client.get_subscription_message(
        name=real_subscription,
        timeout=5,
    )

    assert response is not None
    assert response.body.new["properties"]["univentionObjectIdentifier"]
    uuid.UUID(response.body.new["properties"]["univentionObjectIdentifier"])


async def test_id_is_univention_object_identifier(
    create_user_via_udm_rest_api,
    provisioning_client: ProvisioningConsumerClient,
    real_subscription: str,
):
    univention_object_identifier = str(uuid.uuid4())
    user = create_user_via_udm_rest_api({"univentionObjectIdentifier": univention_object_identifier})  # noqa: F841
    assert univention_object_identifier == user.properties["univentionObjectIdentifier"]

    response = await provisioning_client.get_subscription_message(
        name=real_subscription,
        timeout=5,
    )

    assert response is not None
    assert univention_object_identifier == response.body.new["id"]
    assert "uuid" not in response.body.new
    assert response.body.new["properties"]["univentionObjectIdentifier"]


async def test_get_multiple_messages(
    create_user_via_udm_rest_api, provisioning_client: ProvisioningConsumerClient, real_subscription: str, udm: UDM
):
    user1 = create_user_via_udm_rest_api()  # noqa: F841
    user2 = create_user_via_udm_rest_api()  # noqa: F841
    user3 = create_user_via_udm_rest_api()  # noqa: F841

    result = await pop_all_messages(provisioning_client, real_subscription, 6)
    assert len(result) == 3


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
    extended_attribute, cli_name = create_extended_attribute
    user = create_user_via_udm_rest_api({cli_name: "test@univention.de"})

    message = await provisioning_client.get_subscription_message(
        name=real_subscription,
        timeout=5,
    )
    assert message.body.new.get("dn") == user.dn
    assert message.body.new["properties"][cli_name] == user.properties[cli_name]


async def test_create_user_with_missing_extended_attribute(
    create_user_via_udm_rest_api, provisioning_client: ProvisioningConsumerClient, real_subscription: str
):
    with pytest.raises(UnprocessableEntity, match="The User module has no property ProvisioningServiceEmail."):
        create_user_via_udm_rest_api({"ProvisioningServiceEmail": "test@univention.de"})
