# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.auth import authenticate_admin
from shared.models import Subscription
from shared.services.port import PortDependency
from shared.services.subscriptions import SubscriptionService

router = fastapi.APIRouter()
shared_route = fastapi.APIRouter()
security = HTTPBasic()


@router.get(
    "/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscription(
    name: str,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    port: PortDependency,
) -> Subscription:
    """Return information about a subscription."""

    service = SubscriptionService(port)
    await service.authenticate_user(credentials, name)

    try:
        return await service.get_subscription(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@shared_route.delete("/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK)
async def delete_subscription(
    name: str,
    port: PortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Delete a subscription."""

    service = SubscriptionService(port)

    try:
        authenticate_admin(credentials)
    except HTTPException:
        await service.authenticate_user(credentials, name)

    try:
        await service.delete_subscription(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))