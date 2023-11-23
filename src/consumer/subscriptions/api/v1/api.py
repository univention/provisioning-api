import logging
from typing import List

import fastapi
import shared.models
from consumer.port import ConsumerPortDependency

from consumer.subscriptions.service.subscription import SubscriptionService
from consumer.subscriptions.subscription.sink import SinkManager
from prefill import init_queue as init_prefill_queue

logger = logging.getLogger(__name__)

router = fastapi.APIRouter()
manager = SinkManager()


@router.get("/subscription/", status_code=fastapi.status.HTTP_200_OK, tags=["admin"])
async def get_subscriptions(
    port: ConsumerPortDependency,
) -> List[shared.models.Subscriber]:
    """Return all subscriptions."""

    # TODO: check authorization

    service = SubscriptionService(port)
    return await service.get_subscribers()


@router.get(
    "/subscription/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def get_subscription(
    name: str, port: ConsumerPortDependency
) -> shared.models.Subscriber:
    """Return information about a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

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
    port: ConsumerPortDependency,
    tasks: fastapi.BackgroundTasks,
):
    """Create a new subscription."""

    # TODO: check authorization for `new_sub.subscriber_name` / `new_sub.realms_topics`

    service = SubscriptionService(port)

    try:
        await service.create_subscription(subscriber)
    except ValueError as err:
        raise fastapi.HTTPException(
            fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY, str(err)
        )

    if subscriber.fill_queue:
        tasks.add_task(
            init_prefill_queue,
            subscriber.name,
            subscriber.realm_topic,
        )


@router.delete(
    "/subscription/{name}", status_code=fastapi.status.HTTP_200_OK, tags=["sink"]
)
async def cancel_subscription(name: str, port: ConsumerPortDependency):
    """Delete a subscription."""

    # TODO: check authorization

    service = SubscriptionService(port)

    try:
        await manager.close(name)
        await service.delete_subscriber(name)
    except ValueError as err:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND, str(err))
