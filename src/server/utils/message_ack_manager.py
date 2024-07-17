# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)


class MessageAckManager:
    def __init__(self, ack_wait: int, ack_threshold: int):
        self.ack_wait = ack_wait
        self.ack_threshold = ack_threshold

    async def process_message_with_ack_wait_extension(
        self,
        message_handler: Coroutine[Any, Any, None],
        acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]],
    ):
        """
        Combines message processing and automatic AckWait extension.
        """

        message_handler_task = asyncio.create_task(message_handler)
        ack_extender = asyncio.create_task(self.extend_ack_wait(acknowledge_message_in_progress))

        await message_handler_task

        ack_extender.cancel()

    async def extend_ack_wait(self, acknowledge_message_in_progress: Callable[[], Coroutine[Any, Any, None]]):
        while True:
            await asyncio.sleep(self.ack_wait - self.ack_threshold)
            await acknowledge_message_in_progress()
            logger.info("AckWait was extended")
