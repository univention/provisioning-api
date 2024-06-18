# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Annotated, Optional

import fastapi
import logging

from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from univention.provisioning.models import (
    MessageProcessingStatusReport,
    ProvisioningMessage,
)
from server.services.messages import MessageService
from server.services.port import PortDependency
from server.services.subscriptions import SubscriptionService

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
security = HTTPBasic()


@router.post(
    "/subscriptions/{name}/messages-status",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["subscriptions"],
)
async def post_message_status(
    name: str,
    report: MessageProcessingStatusReport,
    port: PortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Report on the processing of the given message."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)

    try:
        await msg_service.post_message_status(name, report)
    except ValueError as err:
        logger.debug("Failed to post message status: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.get(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["subscriptions"],
)
async def get_next_message(
    name: str,
    port: PortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    timeout: float = 5,
    pop: bool = False,
) -> Optional[ProvisioningMessage]:
    """Return the next pending message for the given subscription."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)
    return await msg_service.get_next_message(name, timeout, pop)
