# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import secrets
from typing import List, Annotated

import fastapi
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasicCredentials, HTTPBasic

from consumer.messages.service import MessageService
from consumer.port import ConsumerPortDependency
from consumer.subscriptions.service.subscription import SubscriptionService
from shared.config import settings
from shared.models import Message, FillQueueStatus

router = fastapi.APIRouter(tags=["internal"], include_in_schema=settings.debug)
security = HTTPBasic()


def authenticate_user(credentials: HTTPBasicCredentials, username: str, password: str):
    is_correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), username.encode("utf8")
    )
    is_correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), password.encode("utf8")
    )
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )


def authenticate_dispatcher(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(
        credentials, settings.dispatcher_username, settings.dispatcher_password
    )


def authenticate_prefill(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(credentials, settings.prefill_username, settings.prefill_password)


def authenticate_udm_producer(
    credentials: Annotated[HTTPBasicCredentials, Depends(security)]
):
    authenticate_user(
        credentials, settings.udm_producer_username, settings.udm_producer_password
    )


@router.get("/subscriptions/filter", status_code=fastapi.status.HTTP_200_OK)
async def get_realm_topic_subscriptions(
    realm_topic: str,
    port: ConsumerPortDependency,
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
    port: ConsumerPortDependency,
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
    port: ConsumerPortDependency,
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
    port: ConsumerPortDependency,
    authentication: Annotated[str, Depends(authenticate_prefill)],
):
    """Create the prefill stream for the subscription."""

    msg_service = MessageService(port)
    await msg_service.create_prefill_stream(name)


@router.patch("/subscriptions/{name}", status_code=fastapi.status.HTTP_200_OK)
async def update_subscription_queue_status(
    name: str,
    prefill_queue_status: FillQueueStatus,
    port: ConsumerPortDependency,
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
    port: ConsumerPortDependency,
    authentication: Annotated[str, Depends(authenticate_udm_producer)],
):
    """Publish a new message to the incoming queue."""

    # TODO: set publisher_name from authentication data

    msg_service = MessageService(port)
    await msg_service.add_live_event(msg)
