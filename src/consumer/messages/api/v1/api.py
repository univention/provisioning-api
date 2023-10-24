import fastapi
import logging

import core.models

from consumer.messages.persistence import (
    DependsMessageRepo,
)
from consumer.messages.service import (
    MessageService,
)
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
    "/subscription/{name}/message/{message_id}",
    status_code=fastapi.status.HTTP_200_OK,
    tags=["sink"],
)
async def post_message_status(
    name: str,
    message_id: str,
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

        await service.remove_message(name, message_id)
    else:
        # message was not processed, nothing to do...
        pass
