# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import fastapi
import logging

from events.service.events import EventsService
from events.port import EventsPortDependency

from shared.models import Message

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


@router.post("/events", status_code=fastapi.status.HTTP_202_ACCEPTED, tags=["source"])
async def create_new_message(
    data: Message,
    port: EventsPortDependency,
):
    """Publish a new message to the incoming queue."""

    # TODO: check authorization

    # TODO: set publisher_name from authentication data

    service = EventsService(port)
    await service.publish_event(data)
