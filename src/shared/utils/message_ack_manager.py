# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
import asyncio
import logging

from shared.models import MQMessage


class MessageAckManager:
    ack_wait = 30
    ack_threshold = 5

    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self._logger = logging.getLogger(__name__)

    async def process_message_with_ack_wait_extension(
        self, message, handle_message, acknowledge_message_in_progress
    ):
        """
        Combines message processing and automatic AckWait extension.
        """

        message_handler = asyncio.create_task(handle_message(message))
        ack_extender = asyncio.create_task(
            self.extend_ack_wait(message, acknowledge_message_in_progress)
        )

        await message_handler

        ack_extender.cancel()

    async def extend_ack_wait(
        self, message: MQMessage, acknowledge_message_in_progress
    ):
        while True:
            await asyncio.sleep(self.ack_wait - self.ack_threshold)
            await acknowledge_message_in_progress(message)
            self._logger.info("AckWait was extended")
