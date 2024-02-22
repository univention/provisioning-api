# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Annotated

import fastapi
import json
import logging

from fastapi import Query

from consumer.messages.service.messages import MessageService
from consumer.port import ConsumerPortDependency

from consumer.subscriptions.subscription.sink import WebSocketSink, SinkManager
from shared.models import (
    MessageProcessingStatusReport,
    MessageProcessingStatus,
    Message,
    ProvisioningMessage,
)

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


@router.post(
    "/subscriptions/{name}/messages-status",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_messages_status(
    subscription_name: str,
    reports: List[MessageProcessingStatusReport],
    port: ConsumerPortDependency,
):
    """Report on the processing of the given messages."""

    # TODO: check authorization

    service = MessageService(port)

    await service.post_message_status(subscription_name, reports)


@router.post(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_message_to_subscription_queue(
    name: str,
    msg: Message,
    port: ConsumerPortDependency,
):
    """Post the message to the subscription's queue."""

    # TODO: check authorization

    service = MessageService(port)
    await service.add_message(name, msg)


@router.get(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def get_subscription_messages(
    name: str,
    port: ConsumerPortDependency,
    count: Annotated[int, Query(ge=1)] = 1,
    timeout: float = 5,
    pop: bool = False,
    skip_prefill: bool = False,
) -> List[ProvisioningMessage]:
    """Return the next pending message(s) for the given subscription."""

    # TODO: check authorization

    service = MessageService(port)
    return await service.get_messages(name, timeout, count, pop, skip_prefill)


@router.post(
    "/subscriptions/{name}/prefill-messages",
    status_code=fastapi.status.HTTP_201_CREATED,
    tags=["sink"],
)
async def post_message_to_subscription_prefill_queue(
    name: str,
    data: Message,
    port: ConsumerPortDependency,
):
    """Post the prefill message to the subscription's prefill queue."""

    # TODO: check authorization

    service = MessageService(port)
    await service.add_prefill_message(name, data)


@router.post(
    "/subscriptions/{name}/prefill-stream",
    status_code=fastapi.status.HTTP_201_CREATED,
    tags=["sink"],
)
async def create_prefill_stream(
    name: str,
    port: ConsumerPortDependency,
):
    """Create the prefill stream for the subscription."""

    # TODO: check authorization

    service = MessageService(port)
    await service.create_prefill_stream(name)


@router.websocket("/subscriptions/{name}/ws")
async def subscription_websocket(
    name: str,
    websocket: fastapi.WebSocket,
    port: ConsumerPortDependency,
):
    """Stream messages for an existing subscription."""

    # TODO: check authorization

    service = MessageService(port)

    sink = await manager.add(name, WebSocketSink(websocket))

    try:
        while True:
            message = await service.get_next_message(name, False, 250)
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
                await service.delete_message(name, report)
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
