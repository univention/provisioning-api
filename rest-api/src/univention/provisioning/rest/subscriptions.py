# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
import time
from typing import Annotated, Optional

import fastapi
from fastapi import Depends, HTTPException, Response

from univention.provisioning.models.message import ProvisioningMessage
from univention.provisioning.models.subscription import Subscription

from .dependencies import AppSettingsDep, HttpBasicDep, authenticate_admin, authenticate_prefill
from .message_service import MessageService
from .models import FillQueueStatusReport, MessageProcessingStatusReport, NewSubscription
from .port import PortDependency
from .subscription_service import SubscriptionService

router = fastapi.APIRouter(prefix="/v1/subscriptions", tags=["subscriptions"])
logger = logging.getLogger(__name__)


@router.get("", status_code=fastapi.status.HTTP_200_OK, dependencies=[Depends(authenticate_admin)])
async def get_subscriptions(port: PortDependency) -> list[Subscription]:
    """Return a list of all known subscriptions."""

    service = SubscriptionService(port)
    return await service.get_subscriptions()


@router.get("/{name}", status_code=fastapi.status.HTTP_200_OK)
async def get_subscription(name: str, credentials: HttpBasicDep, port: PortDependency) -> Subscription:
    """Return information about a subscription."""

    service = SubscriptionService(port)
    await service.authenticate_user(credentials, name)

    try:
        return await service.get_subscription(name)
    except ValueError as err:
        logger.debug("Failed to get subscription: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.delete("/{name}", status_code=fastapi.status.HTTP_200_OK)
async def delete_subscription(name: str, port: PortDependency, credentials: HttpBasicDep, settings: AppSettingsDep):
    """Delete a subscription."""

    service = SubscriptionService(port)

    try:
        authenticate_admin(credentials, settings)
    except HTTPException:
        await service.authenticate_user(credentials, name)

    try:
        await service.delete_subscription(name)
    except ValueError as err:
        logger.debug("Failed to delete subscription: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.post("", status_code=fastapi.status.HTTP_201_CREATED, dependencies=[Depends(authenticate_admin)])
async def create_subscription(subscription: NewSubscription, port: PortDependency, response: Response):
    """Register a new subscription."""

    sub_service = SubscriptionService(port)

    if not await sub_service.register_subscription(subscription):
        response.status_code = fastapi.status.HTTP_200_OK
        return

    if subscription.request_prefill:
        msg_service = MessageService(port)
        await msg_service.send_request_to_prefill(subscription)


@router.patch("/{name}/prefill", status_code=fastapi.status.HTTP_200_OK)
async def update_subscription_prefill_status(
    name: str,
    report: FillQueueStatusReport,
    port: PortDependency,
    authentication: Annotated[None, Depends(authenticate_prefill)],
):
    """Update a subscription's prefill queue status"""

    service = SubscriptionService(port)
    try:
        await service.set_subscription_queue_status(name, report.status)
    except ValueError as err:
        logger.debug("Failed to update subscription queue status: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))


@router.get("/{name}/messages/next", status_code=fastapi.status.HTTP_200_OK)
async def get_next_message(
    name: str, port: PortDependency, credentials: HttpBasicDep, timeout: float = 5, pop: bool = False
) -> Optional[ProvisioningMessage]:
    """Return the next pending message for the given subscription."""

    t0 = time.perf_counter()
    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)
    td0 = time.perf_counter() - t0

    t0 = time.perf_counter()
    msg_service = MessageService(port)
    msg = await msg_service.get_next_message(name, timeout, pop)
    td1 = time.perf_counter() - t0
    timing = f"Auth: {td0 * 1000:.1f} ms, MQ: {td1 * 1000:.1f} ms"
    msg_details = (
        f"new message ({timing}). Publisher: {msg.publisher_name.value} TS: {msg.ts.isoformat()} Realm: {msg.realm} "
        f"Topic: {msg.topic}"
        if msg
        else f"no message ({timing})."
    )
    logger.debug("Got %s", msg_details)
    return msg


@router.patch("/{name}/messages/{seq_num}/status", status_code=fastapi.status.HTTP_200_OK)
async def update_message_status(
    name: str, seq_num: int, report: MessageProcessingStatusReport, port: PortDependency, credentials: HttpBasicDep
):
    """Report on the processing of the given message."""

    sub_service = SubscriptionService(port)
    await sub_service.authenticate_user(credentials, name)

    msg_service = MessageService(port)

    try:
        await msg_service.post_message_status(name, seq_num, report.status)
    except ValueError as err:
        logger.debug("Failed to post message status: %s", err)
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
