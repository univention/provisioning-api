import fastapi
import logging

from events.service.events import EventsService
from events.port import EventsPortDependency

from shared.models import Event

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.post("/events/", status_code=fastapi.status.HTTP_202_ACCEPTED, tags=["source"])
async def create_new_message(
    data: Event,
    request: fastapi.Request,
    port: EventsPortDependency,
):
    """Submit a new message."""

    # TODO: check authorization

    # TODO: set publisher_name from authentication data
    publisher_name = request.client.host

    service = EventsService(port)
    await service.publish_event(data, publisher_name)
