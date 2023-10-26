import fastapi
import logging

from consumer.messages.persistence import DependsMessageRepo
from core.models import NewMessage
from producer.service import MessageService

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.post("/message/", status_code=fastapi.status.HTTP_202_ACCEPTED, tags=["source"])
async def create_new_message(
    data: NewMessage,
    request: fastapi.Request,
    repo: DependsMessageRepo,
):
    """Submit a new message."""

    # TODO: check authorization

    # TODO: set publisher_name from authentication data
    publisher_name = request.client.host

    service = MessageService(repo)
    await service.publish_message(data, publisher_name)