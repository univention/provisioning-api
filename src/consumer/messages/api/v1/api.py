import fastapi
import json
import logging

import core.models

from consumer.messages.persistence import DependsMessageRepo
from consumer.messages.service import MessageService

from consumer.subscriptions.subscription.sink import WebSocketSink
from consumer.subscriptions.subscription.sink import SinkManager


logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


@router.post("/message/", status_code=fastapi.status.HTTP_202_ACCEPTED, tags=["source"])
async def create_new_message(
    data: core.models.NewMessage,
    request: fastapi.Request,
    repo: DependsMessageRepo,
):
    """Submit a new message."""

    # TODO: check authorization

    # TODO: set publisher_name from authentication data
    publisher_name = request.client.host

    service = MessageService(repo)
    await service.publish_message(data, publisher_name)


@router.post(
    "/subscription/{name}/message/{msg_seq_num}",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_message_status(
    name: str,
    msg_seq_num: str,
    repo: DependsMessageRepo,
    report: core.models.MessageProcessingStatusReport,
):
    """Report on the processing of the given message."""

    # TODO: check authorization

    service = MessageService(repo)

    if report.status == core.models.MessageProcessingStatus.ok:
        # Modifying the queue interferes with connected WebSocket clients,
        # so disconnect them first.
        await manager.close(name)

        await service.remove_message(name, msg_seq_num)
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
    repo: DependsMessageRepo,
    count: int = 1,
    timeout: float = 5,
    pop: bool = False,
):
    """Return the next pending message(s) for the given subscription."""

    # TODO: check authorization

    service = MessageService(repo)
    messages = await service.get_messages(name, timeout, count, pop)
    return messages


@router.websocket("/subscription/{name}/ws")
async def subscription_websocket(
    name: str,
    websocket: fastapi.WebSocket,
    repo: DependsMessageRepo,
):
    """Stream messages for an existing subscription."""

    # TODO: check authorization

    service = MessageService(repo)

    sink = await manager.add(name, WebSocketSink(websocket))

    try:
        while True:
            id_message = await service.get_next_message(name, timeout=250)
            if not id_message:
                continue

            msg_seq_num, message = id_message  # FIXME: id_message is not tuple
            await sink.send_message(message)

            reply = await websocket.receive_text()
            try:
                report = core.models.MessageProcessingStatusReport(**json.loads(reply))
            except Exception:
                logger.error(
                    f"{name} > Unexpected input from WebSocket client: {reply}"
                )
                break

            if report.status == core.models.MessageProcessingStatus.ok:
                await service.remove_message(name, msg_seq_num)
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
