# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Annotated

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasic

from server.services.messages import MessageService
from server.services.port import PortDependency
from univention.provisioning.models import Message

from .dependencies import authenticate_events_endpoint

router = fastapi.APIRouter(prefix="/v1/messages", tags=["messages"])
security = HTTPBasic()


@router.post("", status_code=fastapi.status.HTTP_202_ACCEPTED)
async def create_new_message(
    msg: Message,
    port: PortDependency,
    authentication: Annotated[None, Depends(authenticate_events_endpoint)],
):
    """Publish a new message to the incoming queue."""

    # TODO: set publisher_name from authentication data

    msg_service = MessageService(port)
    await msg_service.add_live_event(msg)
