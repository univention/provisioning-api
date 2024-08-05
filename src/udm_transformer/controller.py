# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

from pydantic import ValidationError

from server.adapters.nats_adapter import Acknowledgements, Empty
from server.utils.message_ack_manager import MessageAckManager
from udm_transformer.port import UDMTransformerPort
from udm_transformer.service.udm import UDMMessagingService
from univention.provisioning.models.queue import (
    LDAP_STREAM,
    LDAP_SUBJECT,
    LDIF_STREAM,
    LDIF_SUBJECT,
    Message,
    PublisherName,
)

UDM_TRANSFORMER_CONSUMER_NAME = "udm-transformer"

STREAM = {
    PublisherName.ldif_producer: LDIF_STREAM,
    PublisherName.udm_listener: LDAP_STREAM,
}
SUBJECT = {
    PublisherName.ldif_producer: LDIF_SUBJECT,
    PublisherName.udm_listener: LDAP_SUBJECT,
}

logger = logging.getLogger(__name__)


class UDMTransformerController:
    def __init__(self, port: UDMTransformerPort) -> None:
        self._port = port
        self._udm_service = UDMMessagingService(port)
        # TODO: This needs to be tuned better!
        self.ack_manager = MessageAckManager(ack_wait=30, ack_threshold=5)
        self.ldap_publisher_name = port.settings.ldap_publisher_name

    async def handle_message(self, message: Message, acknowledgements: Acknowledgements) -> None:
        message_handler = self._udm_service.handle_changes(
            message.body.new,
            message.body.old,
            message.ts,
        )
        try:
            await self.ack_manager.process_message_with_ack_wait_extension(
                message_handler,
                acknowledgements.acknowledge_message_in_progress,
            )
        except Exception:
            await acknowledgements.acknowledge_message_negatively()
            raise

    async def transform_events(self) -> None:
        await self._port.initialize_subscription(
            STREAM[self.ldap_publisher_name],
            SUBJECT[self.ldap_publisher_name],
            UDM_TRANSFORMER_CONSUMER_NAME,
        )

        while True:
            logger.debug("listening for new LDAP messages")
            try:
                message, acknowledgements = await self._port.get_one_message(timeout=10)
            except Empty:
                logger.debug("No new LDAP messages found in the queue, continuing to wait.")
                continue
            try:
                validated_message = Message.model_validate(message.data)
            except ValidationError:
                logger.error("Failed to parse the ldap message.")
                raise
            try:
                await self.handle_message(validated_message, acknowledgements)
            except Exception:
                logger.exception("Failed to transform message")
                raise
            await acknowledgements.acknowledge_message()
