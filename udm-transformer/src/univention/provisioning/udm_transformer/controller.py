# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging

from pydantic import ValidationError

from univention.provisioning.backends import Acknowledgements, Empty
from univention.provisioning.models.constants import LDAP_STREAM, LDIF_STREAM, PublisherName
from univention.provisioning.models.message import (
    Message,
)
from univention.provisioning.utils.message_ack_manager import MessageAckManager

from .port import UDMTransformerPort
from .udm import UDMMessagingService

LDAP_SUBJECT = "ldap-producer-subject"
LDIF_SUBJECT = "ldif-producer-subject"
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
        self.ack_manager = MessageAckManager()
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
            False,
            SUBJECT[self.ldap_publisher_name],
        )

        while True:
            logger.debug("listening for new LDAP messages")
            try:
                message, acknowledgements = await self._port.get_one_message(timeout=10)
                data = message.data
                logger.info(
                    "Received message to handle (Publisher: %r Realm: %r Topic: %r TS: %s).",
                    data.get("publisher_name"),
                    data.get("realm"),
                    data.get("topic"),
                    data.get("ts"),
                )
                logger.debug("Message content: %r", data)
            except Empty:
                logger.debug("No new LDAP messages found in the queue, continuing to wait.")
                continue
            try:
                validated_message = Message.model_validate(data)
            except ValidationError:
                logger.error("Failed to parse the ldap message.")
                raise
            try:
                await self.handle_message(validated_message, acknowledgements)
            except Exception:
                logger.exception("Failed to transform message")
                raise
            await acknowledgements.acknowledge_message()
