#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Univention Listener Converter
#  Listener integration
#
# Copyright 2021 Univention GmbH
#
# https://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <https://www.gnu.org/licenses/>.
#
import asyncio

from univention.listener.handler import ListenerModuleHandler

from src.server.core.udm_messaging.port import UDMMessagingPort
from src.server.core.udm_messaging.service.udm import UDMMessagingService

name = "provisioning_handler"


async def handle_changes(new, old):
    async with UDMMessagingPort.port_context() as port:
        service = UDMMessagingService(port)
        await service.handle_changes(new, old)


class LdapListener(ListenerModuleHandler):
    def initialize(self):
        self.logger.info("handler stub initialize")

    def create(self, dn, new):
        self.logger.info("[ create ] dn: %r", dn)
        asyncio.run(handle_changes(new, None))

    def modify(self, dn, old, new, old_dn):
        self.logger.info("[ modify ] dn: %r", dn)
        if old_dn:
            self.logger.debug("it is (also) a move! old_dn: %r", old_dn)
        self.logger.debug("changed attributes: %r", self.diff(old, new))
        asyncio.run(handle_changes(new, old))

    def remove(self, dn, old):
        self.logger.info("[ remove ] dn: %r", dn)
        asyncio.run(handle_changes(None, old))

    class Configuration(ListenerModuleHandler.Configuration):
        name = name
        description = (
            "this listener will be used to send LDAP changes to provisioning consumers"
        )
        ldap_filter = "(objectClass=*)"
