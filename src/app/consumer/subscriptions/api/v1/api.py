# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import Annotated

import fastapi
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.auth import authenticate_admin
from shared.models import Subscription
from shared.services.port import PortDependency
from shared.services.subscriptions import SubscriptionService

router = fastapi.APIRouter()
security = HTTPBasic()
logger = logging.getLogger(__name__)


@router.get(
    "/subscriptions/{name}",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["subscriptions"],
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
        logger.debug("Failed to get subscription: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.delete(
    "/subscriptions/{name}",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["subscriptions"],
)
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
        logger.debug("Failed to delete subscription: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
