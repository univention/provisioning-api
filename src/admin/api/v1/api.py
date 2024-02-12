# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List

import fastapi

from admin.port import AdminPortDependency
from admin.service import AdminService
from shared.models import Subscription, NewSubscription

router = fastapi.APIRouter()


@router.get("/subscriptions", status_code=fastapi.status.HTTP_200_OK, tags=["admin"])
async def get_subscriptions(
    port: AdminPortDependency,
) -> List[Subscription]:
    """Return a list of all known subscriptions."""

    service = AdminService(port)
    return await service.get_subscriptions()


@router.post(
    "/subscriptions", status_code=fastapi.status.HTTP_201_CREATED, tags=["admin"]
)
async def create_subscription(
    subscription: NewSubscription,
    port: AdminPortDependency,
):
    """Create a new subscription."""

    service = AdminService(port)

    try:
        await service.create_subscription(subscription)
    except ValueError as err:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscription.request_prefill:
        await service.send_request_to_prefill(subscription)
