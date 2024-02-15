# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Annotated

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from consumer.port import ConsumerPortDependency

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import FillQueueStatus, Subscription

router = fastapi.APIRouter()
security = HTTPBasic()


@router.get(
    "/subscriptions/filter", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_realm_topic_subscriptions(
    realm_topic: str,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
) -> List[str]:
    """Returns a list of subscriptions names with the given realm_topic."""

    service = SubscriptionService(port)
    await service.authenticate_user(credentials)

    return await service.get_realm_topic_subscriptions(realm_topic)


@router.get(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscription(
    name: str,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    port: ConsumerPortDependency,
) -> Subscription:
    """Return information about a subscription."""

    service = SubscriptionService(port)
    await service.authenticate_user(credentials, name)

    try:
        return await service.get_subscription(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.delete(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def delete_subscription(
    name: str,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Delete a subscription."""

    service = SubscriptionService(port)
    await service.authenticate_user(credentials, name)

    try:
        await service.delete_subscription(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.patch(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def update_subscription_queue_status(
    name: str,
    prefill_queue_status: FillQueueStatus,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Update subscription's prefill queue status"""

    service = SubscriptionService(port)
    await service.authenticate_user(credentials, name)

    try:
        await service.set_subscription_queue_status(name, prefill_queue_status)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
