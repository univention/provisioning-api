import fastapi
import logging

from events.service.messages import MessageService
from events.port import EventsPortDependency

from shared.models import NewMessage

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.post("/events/", status_code=fastapi.status.HTTP_202_ACCEPTED, tags=["source"])
async def create_new_message(
    data: NewMessage,
    request: fastapi.Request,
    port: EventsPortDependency,
):
    """Submit a new message."""

    # TODO: check authorization

    # TODO: set publisher_name from authentication data
    publisher_name = request.client.host

    service = MessageService(port)
    await service.publish_message(data, publisher_name)
