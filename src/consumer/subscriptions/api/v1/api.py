# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Union

import fastapi
import shared.models
from consumer.port import ConsumerPortDependency

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus
from shared.models.subscription import Subscriber

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.get("/subscribers", status_code=fastapi.status.HTTP_200_OK, tags=["admin"])
async def get_subscribers(port: ConsumerPortDependency) -> List[Union[Subscriber, str]]:
    """Return a list of all known subscribers."""

    # TODO: check authorization

    service = SubscriptionService(port)
    return await service.get_subscribers()


@router.get(
    "/subscribers/filter", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_realm_topic_subscribers(
    port: ConsumerPortDependency, realm_topic: str
) -> List[str]:
    """Returns a list of subscriber names with the given realm_topic."""

    # TODO: check authorization

    service = SubscriptionService(port)
    return await service.get_realm_topic_subscribers(realm_topic)


@router.get(
    "/subscribers/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscriber(name: str, port: ConsumerPortDependency) -> Subscriber:
    """Return information about a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        return await service.get_subscriber_info(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.post(
    "/subscriptions", status_code=fastapi.status.HTTP_201_CREATED, tags=["sink"]
)
async def create_subscription(
    subscriber: shared.models.NewSubscription,
    port: ConsumerPortDependency,
):
    """Create a new subscription."""

    # TODO: check authorization for `new_sub.subscriber_name` / `new_sub.realms_topics`

    service = SubscriptionService(port)

    try:
        await service.create_subscription(subscriber)
    except ValueError as err:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscriber.request_prefill:
        await service.send_request_to_prefill(subscriber)


@router.delete(
    "/subscribers/{name}/subscriptions",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def cancel_subscription(
    name: str, realm_topic: str, port: ConsumerPortDependency
):
    """Delete a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        await service.cancel_subscription(name, realm_topic)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.patch(
    "/subscribers/{name}/subscriptions",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def update_subscription_queue_status(
    name: str,
    realm_topic: str,
    prefill_queue_status: FillQueueStatus,
    port: ConsumerPortDependency,
):
    """Update subscription's prefill queue status"""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        await service.set_subscription_queue_status(
            name, realm_topic, prefill_queue_status
        )
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
