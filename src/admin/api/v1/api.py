# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import secrets
from typing import List, Annotated

import fastapi
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from admin.port import AdminPortDependency
from admin.service import AdminService
from shared.config import settings
from shared.models import Subscription, NewSubscription

security = HTTPBasic()


def authenticate_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), settings.admin_username.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), settings.admin_password.encode("utf8")
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


router = fastapi.APIRouter(
    tags=["admin"],
    dependencies=[Depends(authenticate_user)],
    include_in_schema=settings.debug,
)


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
