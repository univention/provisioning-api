#!/usr/bin/python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import asyncio

from univention.listener.handler import ListenerModuleHandler
from univention.provisioning.listener.config import ldap_producer_settings
from univention.provisioning.listener.mq_adapter_nats import MessageQueueNatsAdapter
from univention.provisioning.listener.mq_port import MessageQueuePort

name = "provisioning_handler"


class LdapListener(ListenerModuleHandler):
    class Configuration(ListenerModuleHandler.Configuration):
        name = name
        description = "Listener module that forwards LDAP changes to the UDM Transformer."
        ldap_filter = "(objectClass=*)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mq: MessageQueuePort = MessageQueueNatsAdapter(ldap_producer_settings())
        self._ensure_queue_exists()

    def create(self, dn, new):
        self.logger.info("[ create ] dn: %r", dn)
        self._send_message(new, {})

    def modify(self, dn, old, new, old_dn):
        if old_dn:
            self.logger.info("[ modify & move ] dn: %r old_dn: %r", dn, old_dn)
        else:
            self.logger.info("[ modify ] dn: %r", dn)
        self.logger.debug("changed attributes: %r", self.diff(old, new))
        self._send_message(new, old)

    def remove(self, dn, old):
        self.logger.info("[ remove ] dn: %r", dn)
        self._send_message({}, old)

    def _ensure_queue_exists(self) -> None:
        asyncio.run(self._async_ensure_queue_exists())

    async def _async_ensure_queue_exists(self) -> None:
        async with self.mq as mq:
            await mq.ensure_queue_exists()

    def _send_message(self, new, old) -> None:
        asyncio.run(self._async_send_message(new, old))

    async def _async_send_message(self, new, old) -> None:
        async with self.mq as mq:
            await mq.enqueue_change_event(new, old)
