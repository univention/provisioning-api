# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List, Optional

import fastapi
import shared.models
from consumer.port import ConsumerPortDependency

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.get("/subscriptions", status_code=fastapi.status.HTTP_200_OK, tags=["admin"])
async def get_subscriptions(
    port: ConsumerPortDependency, realm_topic: Optional[str] = None
) -> List[shared.models.Subscriber]:
    """Return a list of all known subscribers or with the given realm_topic."""

    # TODO: check authorization

    service = SubscriptionService(port)
    return await service.get_subscribers(realm_topic)


@router.get(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscription(
    name: str, port: ConsumerPortDependency
) -> shared.models.Subscriber:
    """Return information about a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        subscriber = await service.get_subscriber(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))

    return subscriber


@router.post(
    "/subscriptions", status_code=fastapi.status.HTTP_201_CREATED, tags=["sink"]
)
async def create_subscription(
    subscriber: shared.models.NewSubscriber,
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
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def cancel_subscription(
    name: str, realm: str, topic: str, port: ConsumerPortDependency
):
    """Delete a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        await service.cancel_subscription(name, f"{realm}:{topic}")
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.patch(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def update_subscriber_queue_status(
    name: str, prefill_queue_status: FillQueueStatus, port: ConsumerPortDependency
):
    """Update subscriber's prefill queue status"""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        await service.set_subscriber_queue_status(name, prefill_queue_status)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
