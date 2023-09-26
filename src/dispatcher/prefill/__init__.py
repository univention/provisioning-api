import logging
from typing import List, Tuple

import core.models

from dispatcher.persistence.messages import MessageRepository
from dispatcher.persistence.redis import redis_context
from dispatcher.persistence.subscriptions import SubscriptionRepository
from dispatcher.service.messages import MessageService
from dispatcher.service.subscription import SubscriptionService
from dispatcher.prefill.udm import UDMPreFill


logger = logging.getLogger(__name__)

mapping = {
    "udm": UDMPreFill,
}


async def init_queue(subscriber_name: str, realms_topics: List[Tuple[str, str]]):
    """
    Initialize the queue for the given subscriber with its requested topics.
    """

    logger.debug(f"Initializing queue for {subscriber_name}.")

    async with redis_context() as redis:
        msg_repo = MessageRepository(redis)
        msg_service = MessageService(msg_repo)
        sub_repo = SubscriptionRepository(redis)
        sub_service = SubscriptionService(sub_repo)

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