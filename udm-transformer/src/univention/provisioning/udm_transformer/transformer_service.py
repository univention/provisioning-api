# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import datetime
import json
import logging
from typing import Any, Optional

from pydantic import ValidationError

from univention.provisioning.backends.message_queue import Empty, MessageAckManager
from univention.provisioning.backends.nats_mq import LdapQueue
from univention.provisioning.models.message import Body, EmptyBodyError, Message, NoUDMTypeError

from .cache_port import Cache
from .config import UDMTransformerSettings, udm_transformer_settings
from .event_sender_port import EventSender
from .ldap2udm_port import Ldap2Udm
from .subscriptions_port import SubscriptionsPort

UDM_OBJECT_TYPE_FIELD = "objectType"

logger = logging.getLogger(__name__)


class TransformerService:
    def __init__(
        self,
        ack_manager: MessageAckManager,
        cache: Cache,
        event_sender: EventSender,
        ldap2udm: Ldap2Udm,
        subscriptions: SubscriptionsPort,
        settings: Optional[UDMTransformerSettings] = None,
    ) -> None:
        self.ack_manager = ack_manager
        self.cache = cache
        self.event_sender = event_sender
        self.ldap2udm = ldap2udm
        self.subscriptions = subscriptions
        self.settings = settings or udm_transformer_settings()

    async def listen_for_ldap_events(self) -> None:
        await self.subscriptions.initialize_subscription(LdapQueue())

        while True:
            logger.debug("Listening for new LDAP messages.")
            try:
                message, acknowledgements = await self.subscriptions.get_one_message(timeout=10)
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
                message_handler = self.handle_message(data)
                await self.ack_manager.process_message_with_ack_wait_extension(
                    message_handler,
                    acknowledgements.acknowledge_message_in_progress,
                )
            except Exception:
                await acknowledgements.acknowledge_message_negatively()
                raise
            await acknowledgements.acknowledge_message()

    async def handle_message(self, data: dict[str, Any]):
        try:
            validated_message = Message.model_validate(data)
        except EmptyBodyError:
            logger.warning("Ignoring LDAP message with empty 'new' and 'old'.")
            return
        except NoUDMTypeError:
            logger.warning("Ignoring LDAP message without UDM object type.")
            return
        except ValidationError as exc:
            logger.error("Failed to parse an LDAP message: %s", exc)
            raise
        await self.handle_change(
            validated_message.body.new,
            validated_message.body.old,
            validated_message.ts,
        )

    async def handle_change(
        self, new_ldap_obj: dict[str, Any], old_ldap_obj: dict[str, Any], ts: datetime.datetime
    ) -> None:
        old_udm_obj = await self.old_ldap_to_udm_obj(old_ldap_obj)
        new_udm_obj = await self.new_ldap_to_udm_obj(new_ldap_obj)

        if not new_udm_obj and not old_udm_obj:
            raise RuntimeError("Both 'new' and 'old' UDM objects empty.")

        self.ldap2udm.reload_udm_if_required(new_udm_obj or old_udm_obj)

        message = self.objects_to_message(new_udm_obj, old_udm_obj, ts)
        logger.debug("Sending the message with body: %r", message.body)
        await self.event_sender.send_event(message)
        logger.info("Message was sent: %r", new_udm_obj.get("dn") or old_udm_obj.get("dn"))

    async def old_ldap_to_udm_obj(self, old_ldap_obj: dict[str, Any]) -> dict[str, Any]:
        if not old_ldap_obj:
            return {}
        result = await self.cache.retrieve(old_ldap_obj["entryUUID"][0].decode())
        if not result:
            logger.info("Did not find old_ldap_object in the cache. Falling back to new ldap object.")
            result = self.ldap2udm.ldap_to_udm(old_ldap_obj)
        if not result:
            raise RuntimeError("Cannot live transform old ldap object")
        return result

    async def new_ldap_to_udm_obj(self, new_ldap_obj: dict[str, Any]) -> dict[str, Any]:
        if new_ldap_obj:
            new_udm_obj = self.ldap2udm.ldap_to_udm(new_ldap_obj)
            if new_udm_obj:
                await self.cache.store(new_udm_obj["uuid"], json.dumps(new_udm_obj))
            return new_udm_obj
        return {}

    def objects_to_message(
        self, new_udm_obj: dict[str, Any], old_udm_obj: dict[str, Any], ts: datetime.datetime
    ) -> Message:
        return Message(
            publisher_name=self.settings.ldap_publisher_name,
            ts=ts,
            realm="udm",
            topic=new_udm_obj.get(UDM_OBJECT_TYPE_FIELD) or old_udm_obj.get(UDM_OBJECT_TYPE_FIELD),
            body=Body(old=old_udm_obj, new=new_udm_obj),
        )
