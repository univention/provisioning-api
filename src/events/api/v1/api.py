import fastapi
import logging

from consumer.messages.persistence import DependsMessageRepo
from core.models import NewMessage
from events.service import EventsService

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.post("/events/", status_code=fastapi.status.HTTP_202_ACCEPTED, tags=["source"])
async def publish_event(
    data: NewMessage,
    request: fastapi.Request,
    repo: DependsMessageRepo,
):
    """Submit a new message."""

    # TODO: check authorization

    # TODO: set publisher_name from authentication data
    publisher_name = request.client.host

    service = EventsService()
    await service.publish_event(data, publisher_name)