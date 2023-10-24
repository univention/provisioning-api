import json
import logging
from typing import List, Tuple

import fastapi
import core.models

from consumer.messages.persistence import (
    DependsMessageRepo,
    DependsSubscriptionRepo,
)
from consumer.messages.service import (
    MessageService,
    SubscriptionService,
)
from consumer.messages.subscription.sink import WebSocketSink, SinkManager


logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


@router.get("/subscription/", status_code=fastapi.status.HTTP_200_OK, tags=["admin"])
async def get_subscriptions(
    repo: DependsSubscriptionRepo,
) -> List[core.models.Subscriber]:
    """Return all subscriptions."""

    # TODO: check authorization

    service = SubscriptionService(repo)
    return await service.get_subscribers()


@router.get(
    "/subscription/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscription(
    name: str,
    repo: DependsSubscriptionRepo,
) -> core.models.Subscriber:
    """Return information about a subscription."""

    # TODO: check authorization

    service = SubscriptionService(repo)
    try:
        subscriber = await service.get_subscriber(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))

    return subscriber


@router.post(
    "/subscription/", status_code=fastapi.status.HTTP_201_CREATED, tags=["sink"]
)
async def create_subscription(
    subscriber: core.models.NewSubscriber,
    repo: DependsSubscriptionRepo,
    tasks: fastapi.BackgroundTasks,
):
    """Create a new subscription."""

    # TODO: check authorization for `new_sub.subscriber_name` / `new_sub.realms_topics`

    service = SubscriptionService(repo)

    try:
        await service.add_subscriber(subscriber)
    except ValueError as err:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscriber.fill_queue:
        tasks.add_task(
            dispatcher.prefill.init_queue,
            subscriber.name,
            subscriber.realms_topics,
        )


@router.delete(
    "/subscription/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def cancel_subscription(
    name: str,
    repo: DependsSubscriptionRepo,
):
    """Delete a subscription."""

    # TODO: check authorization

    service = SubscriptionService(repo)
    try:
        await manager.close(name)
        await service.remove_subscriber(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


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
            id_message = await service.get_next_message(name, block=250)
            if not id_message:
                continue

            message_id, message = id_message
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
                await service.remove_message(name, message_id)
            else:
                logger.error(
                    f"{name} > WebSocket client reported status: {report.status}"
                )
                break
    except fastapi.WebSocketDisconnect:
        logger.info(f"{name} WebSocket client disconnected.")
    except Exception as exc:
        logger.warn(f"{name} WebSocket failed: {exc}")
    finally:
        await manager.close(name)


@router.get(
    "/subscription/{name}/message",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def get_subscription_messages(
    name: str,
    repo: DependsMessageRepo,
    count: int | None = None,
    first: int | str | None = None,
    last: int | str | None = None,
) -> List[Tuple[str, core.models.Message]]:
    """Return the next pending message(s) for the given subscription."""

    # TODO: check authorization

    service = MessageService(repo)
    messages = await service.get_messages(name, count or 1, first or "-", last or "+")
    return messages
