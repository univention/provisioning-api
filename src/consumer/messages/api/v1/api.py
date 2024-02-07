# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List

import fastapi
import json
import logging

from consumer.messages.service.messages import MessageService
from consumer.port import ConsumerPortDependency

from consumer.subscriptions.subscription.sink import WebSocketSink, SinkManager
from shared.models import (
    MessageProcessingStatusReport,
    MessageProcessingStatus,
)

from shared.models.queue import MQMessage, Message

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


@router.post(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_message_status(
    name: str,
    seq_num_list: List[int],
    port: ConsumerPortDependency,
    report: MessageProcessingStatusReport,
):
    """Report on the processing of the given messages."""

    # TODO: check authorization

    service = MessageService(port)

    if report.status == MessageProcessingStatus.ok:
        # Modifying the queue interferes with connected WebSocket clients,
        # so disconnect them first.

        await service.delete_messages(name, seq_num_list)
    else:
        # message was not processed, nothing to do...
        pass


@router.get(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def get_subscription_messages(
    name: str,
    port: ConsumerPortDependency,
    count: int = 1,
    timeout: float = 5,
    pop: bool = False,
    skip_prefill: bool = False,
) -> List[MQMessage]:
    """Return the next pending message(s) for the given subscription."""

    # TODO: check authorization

    service = MessageService(port)
    return await service.get_messages(name, timeout, count, pop, skip_prefill)


@router.post(
    "/subscriptions/{name}/prefill-messages",
    status_code=fastapi.status.HTTP_201_CREATED,
    tags=["sink"],
)
async def post_message_to_prefill_queue(
    name: str,
    data: Message,
    port: ConsumerPortDependency,
):
    """Create the prefill message for the subscriber."""

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
    """Create the prefill stream for the subscriber."""

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
            mq_msg = await service.get_next_message(name, False, 250)
            if not mq_msg:
                continue

            message = Message(
                publisher_name=mq_msg.data["publisher_name"],
                ts=mq_msg.data["ts"],
                realm=mq_msg.data["realm"],
                topic=mq_msg.data["topic"],
                body=mq_msg.data["body"],
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
                await service.delete_messages(name, [mq_msg.sequence_number])
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
