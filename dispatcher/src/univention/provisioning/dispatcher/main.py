# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio
import logging

from univention.provisioning.backends.message_queue import MessageAckManager
from univention.provisioning.utils.log import setup_logging

from .config import DispatcherSettings, dispatcher_settings_pull, dispatcher_settings_push
from .mq_adapter_nats import NatsMessageQueueAdapter
from .service import DispatcherService
from .subscriptions_adapter_nats import NatsSubscriptionsAdapter

logger = logging.getLogger(__name__)


async def main(settings_pull: DispatcherSettings, settings_push: DispatcherSettings):
    async with NatsMessageQueueAdapter(settings_pull) as mq_pull, NatsMessageQueueAdapter(settings_push) as mq_push, NatsSubscriptionsAdapter(settings_push) as subscriptions:
        service = DispatcherService(ack_manager=MessageAckManager(), mq_pull=mq_pull, mq_push=mq_push, subscriptions=subscriptions)
        await service.run()


def run():
    settings_pull = dispatcher_settings_pull()
    settings_push = dispatcher_settings_push()
    setup_logging(settings_pull.log_level)
    asyncio.run(main(settings_pull, settings_push))


if __name__ == "__main__":
    run()
