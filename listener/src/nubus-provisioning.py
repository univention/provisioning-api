#!/usr/bin/python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

from univention.listener.handler import ListenerModuleHandler
from univention.provisioning.listener.config import ldap_producer_settings
from univention.provisioning.listener.mq_adapter_nats import MessageQueueNatsAdapter
from univention.provisioning.listener.mq_port import MessageQueuePort
from univention.provisioning.models.message import NoUDMTypeError

name = "provisioning_handler"


class LdapListener(ListenerModuleHandler):
    class Configuration(ListenerModuleHandler.Configuration):
        name = name
        description = "Listener module that forwards LDAP changes to the UDM Transformer."
        ldap_filter = "(objectClass=*)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mq: MessageQueuePort = MessageQueueNatsAdapter(ldap_producer_settings())
        self.connected = False
        self._ensure_queue_exists()

    def create(self, dn, new):
        if self.connected:
            self.logger.info("[ create ] dn: %r", dn)
            self._send_message(new, {})
        else:
            self.logger.warning("Not connected to the message queue. Skipping create event for dn: %r", dn)

    def modify(self, dn, old, new, old_dn):
        if self.connected:
            if old_dn:
                self.logger.info("[ modify & move ] dn: %r old_dn: %r", dn, old_dn)
            else:
                self.logger.info("[ modify ] dn: %r", dn)
            self.logger.debug("changed attributes: %r", self.diff(old, new))
            self._send_message(new, old)
        else:
            self.logger.warning("Not connected to the message queue. Skipping create event for dn: %r", dn)

    def remove(self, dn, old):
        if self.connected:
            self.logger.info("[ remove ] dn: %r", dn)
            self._send_message({}, old)
        else:
            self.logger.warning("Not connected to the message queue. Skipping create event for dn: %r", dn)

    def _ensure_queue_exists(self) -> None:
        try:
            asyncio.run(self._async_ensure_queue_exists())
            self.connected = True
        except OSError as exc:
            self.logger.error("Failed to connect to the message queue: %s", exc)

    async def _async_ensure_queue_exists(self) -> None:
        async with self.mq as mq:
            await mq.ensure_queue_exists()

    def _send_message(self, new, old) -> None:
        try:
            asyncio.run(self._async_send_message(new, old))
        except OSError as exc:
            self.logger.error("Failed to send message to the message queue: %s", exc)
            self.connected = False

    async def _async_send_message(self, new, old) -> None:
        async with self.mq as mq:
            try:
                await mq.enqueue_change_event(new, old)
            except NoUDMTypeError:
                self.logger.debug("Ignoring non-UDM messages. new: %r, old: %r", new, old)
