import logging
from typing import List

import fastapi
import shared.models

from consumer.subscriptions.service.subscription import DependsSubscriptionService
from consumer.subscriptions.subscription.sink import SinkManager
from prefill import init_queue as init_prefill_queue


logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


@router.get("/subscription/", status_code=fastapi.status.HTTP_200_OK, tags=["admin"])
async def get_subscriptions(
    service: DependsSubscriptionService,
) -> List[shared.models.Subscriber]:
    """Return all subscriptions."""

    # TODO: check authorization

    return await service.get_subscribers()


@router.get(
    "/subscription/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscription(
    name: str,
    service: DependsSubscriptionService,
) -> shared.models.Subscriber:
    """Return information about a subscription."""

    # TODO: check authorization

    try:
        subscriber = await service.get_subscriber(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))

    return subscriber


@router.post(
    "/subscription/", status_code=fastapi.status.HTTP_201_CREATED, tags=["sink"]
)
async def create_subscription(
    subscriber: shared.models.NewSubscriber,
    service: DependsSubscriptionService,
    tasks: fastapi.BackgroundTasks,
):
    """Create a new subscription."""

    # TODO: check authorization for `new_sub.subscriber_name` / `new_sub.realms_topics`

    try:
        await service.add_subscriber(subscriber)
    except ValueError as err:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscriber.fill_queue:
        tasks.add_task(
            init_prefill_queue,
            subscriber.name,
            subscriber.realms_topics,
        )


@router.delete(
    "/subscription/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def cancel_subscription(
    name: str,
    service: DependsSubscriptionService,
):
    """Delete a subscription."""

    # TODO: check authorization

    try:
        await manager.close(name)
        await service.delete_subscriber(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
