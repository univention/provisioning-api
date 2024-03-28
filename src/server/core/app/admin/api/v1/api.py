# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import List
import fastapi
from fastapi import Depends

from src.server.core.app.auth import authenticate_admin
from src.shared.models import Subscription, NewSubscription
from src.server.services.messages import MessageService
from src.server.services.port import PortDependency
from src.server.services.subscriptions import SubscriptionService

router = fastapi.APIRouter(tags=["admin"], dependencies=[Depends(authenticate_admin)])
logger = logging.getLogger(__name__)


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
        logger.debug("Failed to register subscription: %s", err)
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscription.request_prefill:
        msg_service = MessageService(port)
        await msg_service.send_request_to_prefill(subscription)
