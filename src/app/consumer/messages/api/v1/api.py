# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Annotated

import fastapi
import json
import logging

from fastapi import Query, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.consumer.subscriptions.subscription.sink import SinkManager, WebSocketSink
from shared.models import (
    MessageProcessingStatusReport,
    MessageProcessingStatus,
    Message,
    ProvisioningMessage,
)
from shared.services.messages import MessageService
from shared.services.port import PortDependency
from shared.services.subscriptions import SubscriptionService

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()
security = HTTPBasic()


@router.post(
    "/subscriptions/{name}/messages-status",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["subscriptions"],
)
async def post_messages_status(
    name: str,
    reports: List[MessageProcessingStatusReport],
    port: PortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Report on the processing of the given messages."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)

    await msg_service.post_messages_status(name, reports)


@router.get(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["subscriptions"],
)
async def get_subscription_messages(
    name: str,
    port: PortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    count: Annotated[int, Query(ge=1)] = 1,
    timeout: float = 5,
    pop: bool = False,
    skip_prefill: bool = False,
) -> List[ProvisioningMessage]:
    """Return the next pending message(s) for the given subscription."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)
    return await msg_service.get_messages(name, timeout, count, pop, skip_prefill)


@router.websocket("/subscriptions/{name}/ws")
async def subscription_websocket(
    name: str,
    websocket: fastapi.WebSocket,
    port: PortDependency,
):
    """Stream messages for an existing subscription."""

    msg_service = MessageService(port)

    sink = await manager.add(name, WebSocketSink(websocket))

    try:
        while True:
            message = await msg_service.get_next_message(name, False, 250)
            if not message:
                continue

            await sink.send_message(Message.model_validate(message))

            reply = await websocket.receive_text()
            try:
                report = MessageProcessingStatusReport(**json.loads(reply))
            except Exception:
                logger.error(
                    "%s > Unexpected input from WebSocket client: %s", name, reply
                )
                break

            if report.status == MessageProcessingStatus.ok:
                await msg_service.delete_message(name, report)
            else:
                logger.error(
                    "%s > WebSocket client reported status: %s", name, report.status
                )
                break
    except fastapi.WebSocketDisconnect:
        logger.info("%s WebSocket client disconnected.", name)
    except Exception as exc:
        logger.warning("%s WebSocket failed: %s", name, exc)
    finally:
        await manager.close(name)
