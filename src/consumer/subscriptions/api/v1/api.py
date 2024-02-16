# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Annotated

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from consumer.port import ConsumerPortDependency

from consumer.subscriptions.service.subscription import SubscriptionService
from shared.models import Subscription

router = fastapi.APIRouter()
security = HTTPBasic()


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
