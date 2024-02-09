# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List

import fastapi
from consumer.port import ConsumerPortDependency

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus, Subscription

router = fastapi.APIRouter()


@router.get(
    "/subscriptions/filter", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_realm_topic_subscriptions(
    port: ConsumerPortDependency, realm_topic: str
) -> List[str]:
    """Returns a list of subscriptions names with the given realm_topic."""

    # TODO: check authorization

    service = SubscriptionService(port)
    return await service.get_realm_topic_subscriptions(realm_topic)


@router.get(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscription(name: str, port: ConsumerPortDependency) -> Subscription:
    """Return information about a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        return await service.get_subscription(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.delete(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def delete_subscription(name: str, port: ConsumerPortDependency):
    """Delete a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        await service.delete_subscription(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.patch(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def update_subscription_queue_status(
    name: str, prefill_queue_status: FillQueueStatus, port: ConsumerPortDependency
):
    """Update subscription's prefill queue status"""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        await service.set_subscription_queue_status(name, prefill_queue_status)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
