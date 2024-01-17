# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import List

from consumer.port import ConsumerPort

from consumer.messages.service.messages import MessageService
from consumer.subscriptions.service.subscription import SubscriptionService
from prefill.udm import UDMPreFill
from prefill.port import PrefillPort
from shared.models import FillQueueStatus

logger = logging.getLogger(__name__)

mapping = {
    "udm": UDMPreFill,
}


async def init_queue(subscriber_name: str, realm_topic: List[str]):
    """
    Initialize the queue for the given subscriber with its requested topics.
    """

    logger.debug(f"Initializing queue for {subscriber_name}.")

    async with ConsumerPort.port_context() as consumer_port:
        msg_service = MessageService(consumer_port)
        sub_service = SubscriptionService(consumer_port)

        await sub_service.set_subscriber_queue_status(
            subscriber_name, FillQueueStatus.running
        )

        try:
            logging.debug(f"Initializing {realm_topic[1]} from {realm_topic[0]}.")
            handler_class = mapping.get(realm_topic[0])

            if not handler_class:
                # FIXME: unhandled realm
                logging.error(f"Unhandled realm: {realm_topic[0]}")
                return

            async with PrefillPort.port_context() as prefill_port:
                handler = handler_class(
                    prefill_port, msg_service, subscriber_name, realm_topic[1]
                )
                await handler.fetch()

        except Exception as err:
            import traceback

            traceback.print_exc()
            logging.error(f"Failed to launch pre-fill handler: {err.__class__} {err}")

            await sub_service.set_subscriber_queue_status(
                subscriber_name, FillQueueStatus.failed
            )

        else:
            await sub_service.set_subscriber_queue_status(
                subscriber_name, FillQueueStatus.done
            )
