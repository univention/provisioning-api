# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import logging
from typing import Annotated

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from src.server.core.app.config import app_settings
from src.shared.models import Message, FillQueueStatus
from src.server.core.app.auth import authenticate_user
from src.server.services.messages import MessageService
from src.server.services.port import PortDependency
from src.server.services.subscriptions import SubscriptionService

router = fastapi.APIRouter(tags=["internal"])
security = HTTPBasic()
logger = logging.getLogger(__name__)


def authenticate_prefill(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(
        credentials, app_settings.prefill_username, app_settings.prefill_password
    )


def authenticate_events_endpoint(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(
        credentials,
        app_settings.events_username_udm,
        app_settings.events_password_udm,
    )


@router.patch("/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK)
async def update_subscription_queue_status(
    name: str,
    prefill_queue_status: FillQueueStatus,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_prefill)],
):
    """Update subscription's prefill queue status"""

    service = SubscriptionService(port)
    try:
        await service.set_subscription_queue_status(name, prefill_queue_status)
    except ValueError as err:
        logger.debug("Failed to update subscription queue status: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.post("/events", status_code=fastapi.status.HTTP_202_ACCEPTED)
async def create_new_message(
    msg: Message,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_events_endpoint)],
):
    """Publish a new message to the incoming queue."""

    # TODO: set publisher_name from authentication data

    msg_service = MessageService(port)
    await msg_service.add_live_event(msg)
