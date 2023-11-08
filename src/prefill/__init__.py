import logging
from typing import List, Tuple

import core.models
from consumer.core.persistence.nats import nats_context

from consumer.messages.persistence.messages import MessageRepository
from consumer.core.persistence.redis import redis_context
from consumer.subscriptions.persistence.subscriptions import SubscriptionRepository
from consumer.messages.service.messages import MessageService
from consumer.subscriptions.service.subscription import SubscriptionService
from prefill.udm import UDMPreFill


logger = logging.getLogger(__name__)

mapping = {
    "udm": UDMPreFill,
}


async def init_queue(subscriber_name: str, realms_topics: List[Tuple[str, str]]):
    """
    Initialize the queue for the given subscriber with its requested topics.
    """

    logger.debug(f"Initializing queue for {subscriber_name}.")

    async with redis_context() as redis, nats_context() as nats:
        msg_repo = MessageRepository(redis, nats)
        msg_service = MessageService(msg_repo)
        sub_repo = SubscriptionRepository(redis)
        sub_service = SubscriptionService(sub_repo, msg_repo)

        await sub_service.set_subscriber_queue_status(
            subscriber_name, core.models.FillQueueStatus.running
        )

        try:
            for realm, topic in realms_topics:
                logging.debug(f"Initializing {topic} from {realm}.")
                if handler_class := mapping.get(realm):
                    handler = handler_class(msg_service, subscriber_name, topic)
                    await handler.fetch()
                else:
                    # FIXME: unhandled realm
                    logging.error(f"Unhandled realm: {realm}")

        except Exception as err:
            import traceback

            traceback.print_exc()
            logging.error(f"Failed to launch pre-fill handler: {err.__class__} {err}")

            await sub_service.set_subscriber_queue_status(
                subscriber_name, core.models.FillQueueStatus.failed
            )

        else:
            await sub_service.set_subscriber_queue_status(
                subscriber_name, core.models.FillQueueStatus.done
            )
