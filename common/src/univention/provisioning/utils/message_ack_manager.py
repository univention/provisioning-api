# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


class MessageAckManager:
    def __init__(self, ack_wait: int = 30, ack_threshold: int = 5):
        self.ack_wait = ack_wait
        self.ack_threshold = ack_threshold

    async def process_message_with_ack_wait_extension(
        self,
        message_handler: Coroutine[Any, Any, None],
        acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]],
    ) -> None:
        """
        Combines message processing and automatic AckWait extension.
        """

        async with asyncio.TaskGroup() as task_group:
            ack_extender = task_group.create_task(self.extend_ack_wait(acknowledge_message_in_progress))
            message_handler_task = task_group.create_task(message_handler)

            await message_handler_task
            ack_extender.cancel()

    async def extend_ack_wait(self, acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]]) -> None:
        while True:
            await asyncio.sleep(self.ack_wait - self.ack_threshold)
            await acknowledge_message_in_progress()
            logger.info("AckWait was extended")
