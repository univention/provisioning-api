# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Annotated

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from admin.port import AdminPortDependency
from admin.service import AdminService
from shared.config import settings
from shared.models import Subscription, NewSubscription
from shared.auth import authenticate_user

security = HTTPBasic()


def authenticate_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    authenticate_user(credentials, settings.admin_username, settings.admin_password)


router = fastapi.APIRouter(tags=["admin"], dependencies=[Depends(authenticate_admin)])


@router.get("/subscriptions", status_code=fastapi.status.HTTP_200_OK)
async def get_subscriptions(port: AdminPortDependency) -> List[Subscription]:
    """Return a list of all known subscriptions."""

    service = AdminService(port)
    return await service.get_subscriptions()


@router.post("/subscriptions", status_code=fastapi.status.HTTP_201_CREATED)
async def register_subscription(
    subscription: NewSubscription,
    port: AdminPortDependency,
):
    """Register a new subscription."""

    service = AdminService(port)

    try:
        await service.register_subscription(subscription)
    except ValueError as err:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscription.request_prefill:
        await service.send_request_to_prefill(subscription)
