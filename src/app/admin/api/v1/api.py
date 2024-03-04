# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Annotated

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.config import app_settings
from shared.models import Subscription, NewSubscription
from app.auth import authenticate_user
from shared.services.messages import MessageService
from shared.services.port import PortDependency
from shared.services.subscriptions import SubscriptionService

security = HTTPBasic()


def authenticate_admin(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    authenticate_user(
        credentials, app_settings.admin_username, app_settings.admin_password
    )


router = fastapi.APIRouter(tags=["admin"], dependencies=[Depends(authenticate_admin)])


@router.get("/subscriptions", status_code=fastapi.status.HTTP_200_OK)
async def get_subscriptions(port: PortDependency) -> List[Subscription]:
    """Return a list of all known subscriptions."""

    service = SubscriptionService(port)
    return await service.get_subscriptions()


@router.post("/subscriptions", status_code=fastapi.status.HTTP_201_CREATED)
async def register_subscription(
    subscription: NewSubscription,
    port: PortDependency,
):
    """Register a new subscription."""

    sub_service = SubscriptionService(port)

    try:
        await sub_service.register_subscription(subscription)
    except ValueError as err:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscription.request_prefill:
        msg_service = MessageService(port)
        await msg_service.send_request_to_prefill(subscription)
