# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import secrets
from typing import List, Annotated

import fastapi
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from admin.config import admin_settings
from admin.port import AdminPortDependency
from admin.service import AdminService
from shared.models import Subscription, NewSubscription

router = fastapi.APIRouter()
security = HTTPBasic()


def authenticate_user(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    current_username_bytes = credentials.username.encode("utf8")
    expected_username_bytes = admin_settings.admin_username.encode("utf8")
    is_correct_username = secrets.compare_digest(
        current_username_bytes, expected_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    expected_password_bytes = admin_settings.admin_password.encode("utf8")
    is_correct_password = secrets.compare_digest(
        current_password_bytes, expected_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


@router.get("/subscriptions", status_code=fastapi.status.HTTP_200_OK, tags=["admin"])
async def get_subscriptions(
    authentication: Annotated[str, Depends(authenticate_user)],
    port: AdminPortDependency,
) -> List[Subscription]:
    """Return a list of all known subscriptions."""

    service = AdminService(port)
    return await service.get_subscriptions()


@router.post(
    "/subscriptions", status_code=fastapi.status.HTTP_201_CREATED, tags=["admin"]
)
async def register_subscription(
    subscription: NewSubscription,
    authentication: Annotated[str, Depends(authenticate_user)],
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
