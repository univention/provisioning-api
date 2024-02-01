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
)

from shared.models.queue import NatsMessage, Message, PrefillStream

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


# TODO: fix post_message_status endpoint
# @router.post(
#     "",
#     status_code=fastapi.status.HTTP_200_OK,
#     tags=["sink"],
# )
# async def post_message_status(
#         name: str,
#         msg: Message,
#         port: ConsumerPortDependency,
#         report: MessageProcessingStatusReport,
# ):
#     """Report on the processing of the given message."""
#     # TODO: check authorization
#
#     service = MessageService(port)
#     if report.status == MessageProcessingStatus.ok:
#         # Modifying the queue interferes with connected WebSocket clients,
#         # so disconnect them first.
#         await manager.close(name)
#         await service.remove_message(msg)
#     else:
#         # message was not processed, nothing to do...
#         pass


@router.post(
    "/subscribers/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def create_message(
    name: str,
    msg: Message,
    port: ConsumerPortDependency,
):
    """Create the message for the subscriber."""

    # TODO: check authorization

    service = MessageService(port)
    await service.add_message(name, msg)


@router.get(
    "/subscribers/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def get_subscriber_messages(
    name: str,
    port: ConsumerPortDependency,
    count: Annotated[int, Query(ge=1)] = 1,
    timeout: float = 5,
    pop: bool = False,
    skip_prefill: bool = False,
) -> List[NatsMessage]:
    """Return the next pending message(s) for the given subscription."""

    # TODO: check authorization

    service = MessageService(port)
    return await service.get_messages(name, timeout, count, pop, skip_prefill)


@router.delete(
    "/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def remove_message(
    msg: NatsMessage,
    port: ConsumerPortDependency,
):
    """Remove message."""

    # TODO: check authorization

    service = MessageService(port)
    return await service.remove_message(msg)


@router.post(
    "/subscribers/{name}/prefill-messages",
    status_code=fastapi.status.HTTP_201_CREATED,
    tags=["sink"],
)
async def create_prefill_message(
    name: str,
    data: Message,
    port: ConsumerPortDependency,
):
    """Create the prefill message for the subscriber."""

    # TODO: check authorization

    service = MessageService(port)
    await service.add_prefill_message(name, data)


@router.post(
    "/prefill-streams",
    status_code=fastapi.status.HTTP_201_CREATED,
    tags=["sink"],
)
async def create_prefill_stream(
    data: PrefillStream,
    port: ConsumerPortDependency,
):
    """Create the prefill stream for the subscriptions."""

    # TODO: check authorization

    service = MessageService(port)
    await service.create_prefill_stream(data)


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
            nats_mess = await service.get_next_message(name, False, 250)
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
                    f"{name} > Unexpected input from WebSocket client: {reply}"
                )
                break

            if report.status == MessageProcessingStatus.ok:
                await service.remove_message(nats_mess)
            else:
                logger.error(
                    f"{name} > WebSocket client reported status: {report.status}"
                )
                break
    except fastapi.WebSocketDisconnect:
        logger.info(f"{name} WebSocket client disconnected.")
    except Exception as exc:
        logger.warning(f"{name} WebSocket failed: {exc}")
    finally:
        await manager.close(name)
