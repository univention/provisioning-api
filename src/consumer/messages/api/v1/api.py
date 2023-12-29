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

from shared.models.queue import NatsMessage, Message

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


@router.post(
    "/subscription/{name}/message/",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_message_status(
    name: str,
    msg: NatsMessage,
    port: ConsumerPortDependency,
    report: MessageProcessingStatusReport,
):
    """Report on the processing of the given message."""

    # TODO: check authorization

    service = MessageService(port)

    if report.status == MessageProcessingStatus.ok:
        # Modifying the queue interferes with connected WebSocket clients,
        # so disconnect them first.
        await manager.close(name)

        await service.remove_message(msg)
    else:
        # message was not processed, nothing to do...
        pass


@router.get(
    "/subscription/{name}/message",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def get_subscription_messages(
    name: str,
    port: ConsumerPortDependency,
    count: int = 1,
    timeout: float = 5,
    pop: bool = False,
    force: bool = False,
) -> List[NatsMessage]:
    """Return the next pending message(s) for the given subscription."""

    # TODO: check authorization

    service = MessageService(port)
    return await service.get_messages(name, timeout, count, pop, force)


@router.delete(
    "/message/",
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


@router.websocket("/subscription/{name}/ws")
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
                    "%s > Unexpected input from WebSocket client: %s", name, reply
                )
                break

            if report.status == MessageProcessingStatus.ok:
                await service.remove_message(nats_mess)
            else:
                logger.error(
                    "%s > WebSocket client reported status: %s", name, report.status
                )
                break
    except fastapi.WebSocketDisconnect:
        logging.info("%s WebSocket client disconnected.", name)
    except Exception as exc:
        logger.warning("%s WebSocket failed: %s", name, exc)
    finally:
        await manager.close(name)
