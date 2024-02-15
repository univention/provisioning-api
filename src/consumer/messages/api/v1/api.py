# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Annotated

import fastapi
import json
import logging

from fastapi import Query, Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from consumer.messages.service.messages import MessageService
from consumer.port import ConsumerPortDependency
from consumer.subscriptions.service.subscription import SubscriptionService

from consumer.subscriptions.subscription.sink import WebSocketSink, SinkManager
from shared.models import (
    MessageProcessingStatusReport,
    MessageProcessingStatus,
    MQMessage,
    Message,
)

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()
security = HTTPBasic()


@router.post(
    "/subscriptions/{name}/messages-status",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_message_status(
    name: str,
    msg: MQMessage,
    report: MessageProcessingStatusReport,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Report on the processing of the given message."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)

    if report.status == MessageProcessingStatus.ok:
        # Modifying the queue interferes with connected WebSocket clients,
        # so disconnect them first.
        await manager.close(name)

        await msg_service.remove_message(msg)
    else:
        # message was not processed, nothing to do...
        pass


@router.post(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_message_to_subscription_queue(
    name: str,
    msg: Message,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Post the message to the subscription's queue."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)
    await msg_service.add_message(name, msg)


@router.get(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def get_subscription_messages(
    name: str,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
    count: Annotated[int, Query(ge=1)] = 1,
    timeout: float = 5,
    pop: bool = False,
    skip_prefill: bool = False,
) -> List[MQMessage]:
    """Return the next pending message(s) for the given subscription."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)
    return await msg_service.get_messages(name, timeout, count, pop, skip_prefill)


@router.delete(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def remove_message(
    name: str,
    msg: MQMessage,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Remove message."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)
    return await msg_service.remove_message(msg)


@router.post(
    "/subscriptions/{name}/prefill-messages",
    status_code=fastapi.status.HTTP_201_CREATED,
    tags=["sink"],
)
async def post_message_to_subscription_prefill_queue(
    name: str,
    data: Message,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Post the prefill message to the subscription's prefill queue."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)
    await msg_service.add_prefill_message(name, data)


@router.post(
    "/subscriptions/{name}/prefill-stream",
    status_code=fastapi.status.HTTP_201_CREATED,
    tags=["sink"],
)
async def create_prefill_stream(
    name: str,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Create the prefill stream for the subscription."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)
    await msg_service.create_prefill_stream(name)


@router.websocket("/subscriptions/{name}/ws")
async def subscription_websocket(
    name: str,
    websocket: fastapi.WebSocket,
    port: ConsumerPortDependency,
    credentials: Annotated[HTTPBasicCredentials, Depends(security)],
):
    """Stream messages for an existing subscription."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)

    sink = await manager.add(name, WebSocketSink(websocket))

    try:
        while True:
            nats_mess = await msg_service.get_next_message(name, False, 250)
            if not nats_mess:
                continue

            message = Message(
                publisher_name=nats_mess.data["publisher_name"],
                ts=nats_mess.data["ts"],
                realm=nats_mess.data["realm"],
                topic=nats_mess.data["topic"],
                body=nats_mess.data["body"],
            )
            await sink.send_message(message)

            reply = await websocket.receive_text()
            try:
                report = MessageProcessingStatusReport(**json.loads(reply))
            except Exception:
                logger.error(
                    "%s > Unexpected input from WebSocket client: %s", name, reply
                )
                break

            if report.status == MessageProcessingStatus.ok:
                await msg_service.remove_message(nats_mess)
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
