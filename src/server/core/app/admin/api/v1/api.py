# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import List

import fastapi
from fastapi import Depends, Response, status

from server.core.app.auth import authenticate_admin
from server.services.messages import MessageService
from server.services.port import PortDependency
from server.services.subscriptions import SubscriptionService
from univention.provisioning.models import NewSubscription, Subscription

router = fastapi.APIRouter(tags=["admin"], dependencies=[Depends(authenticate_admin)])
logger = logging.getLogger(__name__)


@router.get("/subscriptions", status_code=fastapi.status.HTTP_200_OK)
async def get_subscriptions(port: PortDependency) -> List[Subscription]:
    """Return a list of all known subscriptions."""

    service = SubscriptionService(port)
    return await service.get_subscriptions()


@router.post("/subscriptions", status_code=fastapi.status.HTTP_201_CREATED)
async def register_subscription(subscription: NewSubscription, port: PortDependency, response: Response):
    """Register a new subscription."""

    sub_service = SubscriptionService(port)

    if not await sub_service.register_subscription(subscription):
        response.status_code = status.HTTP_200_OK
        return

    if subscription.request_prefill:
        msg_service = MessageService(port)
        await msg_service.send_request_to_prefill(subscription)
