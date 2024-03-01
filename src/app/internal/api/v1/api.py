# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import List, Annotated

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from app.config import app_settings
from shared.models import Message, FillQueueStatus
from shared.auth import authenticate_user
from shared.services.messages import MessageService
from shared.services.port import PortDependency
from shared.services.subscriptions import SubscriptionService

router = fastapi.APIRouter(tags=["internal"])
security = HTTPBasic()


def authenticate_dispatcher(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(
        credentials, app_settings.dispatcher_username, app_settings.dispatcher_password
    )


def authenticate_prefill(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(
        credentials, app_settings.prefill_username, app_settings.prefill_password
    )


def authenticate_udm_listener(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(
        credentials,
        app_settings.udm_listener_username,
        app_settings.udm_listener_password,
    )


@router.get("/subscriptions/filter", status_code=fastapi.status.HTTP_200_OK)
async def get_realm_topic_subscriptions(
    realm_topic: str,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_dispatcher)],
) -> List[str]:
    """Returns a list of subscriptions names with the given realm_topic."""

    service = SubscriptionService(port)

    return await service.get_realm_topic_subscriptions(realm_topic)


@router.post(
    "/subscriptions/{name}/messages",
    status_code=fastapi.status.HTTP_200_OK,
)
async def post_message_to_subscription_queue(
    name: str,
    msg: Message,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_dispatcher)],
):
    """Post the message to the subscription's queue."""

    msg_service = MessageService(port)
    await msg_service.add_message(name, msg)


@router.post(
    "/subscriptions/{name}/prefill-messages",
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def post_message_to_subscription_prefill_queue(
    name: str,
    data: Message,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_prefill)],
):
    """Post the prefill message to the subscription's prefill queue."""

    msg_service = MessageService(port)
    await msg_service.add_prefill_message(name, data)


@router.post(
    "/subscriptions/{name}/prefill-stream",
    status_code=fastapi.status.HTTP_201_CREATED,
)
async def create_prefill_stream(
    name: str,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_prefill)],
):
    """Create the prefill stream for the subscription."""

    msg_service = MessageService(port)
    await msg_service.create_prefill_stream(name)


@router.patch("/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK)
async def update_subscription_queue_status(
    name: str,
    prefill_queue_status: FillQueueStatus,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_prefill)],
):
    """Update subscription's prefill queue status"""

    service = SubscriptionService(port)
    try:
        await service.set_subscription_queue_status(name, prefill_queue_status)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.post("/events", status_code=fastapi.status.HTTP_202_ACCEPTED)
async def create_new_message(
    msg: Message,
    port: PortDependency,
    authentication: Annotated[str, Depends(authenticate_udm_listener)],
):
    """Publish a new message to the incoming queue."""

    # TODO: set publisher_name from authentication data

    msg_service = MessageService(port)
    await msg_service.add_live_event(msg)
