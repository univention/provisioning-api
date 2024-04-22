#!/usr/bin/env -S python3 -O
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
#
# Like what you see? Join us!
# https://www.univention.com/about-us/careers/vacancies/
#
# Copyright 2024 Univention GmbH
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

import logging
import os
import sys

from slapdsock.service import SlapdSockServer
from slapdsock.handler import SlapdSockHandler
from slapdsock.message import CONTINUE_RESPONSE

PARALLEL_REQUESTS_MAX = 4


class ReasonableSlapdSockHandler(SlapdSockHandler):
    def __call__(self, *args, **kwargs):
        """
        Handle a request.

        See https://stackoverflow.com/questions/21631799/how-can-i-pass-parameters-to-a-requesthandler
        """
        super().__init__(*args, **kwargs)


class LDAPHandler(ReasonableSlapdSockHandler):
    """
    This handler simply returns CONTINUE+LF for every sockops request
    and empty string for sockresps and unbind requests.

    This is handy to be used as safe base class for own custom handler
    to make sure each back-sock request is always answered in
    case of misconfigured "overlay sock" section.
    """

    def __init__(self, ldap_base):
        self.req_queue = {}
        temporary_dn_string = ",cn=temporary,cn=univention,"
        self.len_temporary_dn_suffix = len(temporary_dn_string) + len(ldap_base)

    def is_temporary_dn(self, request):
        return "," in request.dn[self.len_temporary_dn_suffix :]

    def do_add(self, request):
        """
        ADD
        """
        if self.is_temporary_dn(request):
            return CONTINUE_RESPONSE
        self._log(logging.DEBUG, "do_add = %s", request)
        self.req_queue[(request.connid, request.msgid)] = request
        return CONTINUE_RESPONSE

    def do_bind(self, request):
        """
        BIND
        """
        self._log(logging.DEBUG, "do_bind = %s", request)
        return CONTINUE_RESPONSE

    def do_compare(self, request):
        """
        COMPARE
        """
        _ = (self, request)  # pylint dummy
        return CONTINUE_RESPONSE

    def do_delete(self, request):
        """
        DELETE
        """
        if self.is_temporary_dn(request):
            return CONTINUE_RESPONSE
        self._log(logging.DEBUG, "do_delete = %s", request)
        self.req_queue[(request.connid, request.msgid)] = request
        return CONTINUE_RESPONSE

    def do_modify(self, request):
        """
        MODIFY
        """
        if self.is_temporary_dn(request):
            return CONTINUE_RESPONSE
        self._log(logging.DEBUG, "do_modify = %s", request)
        self.req_queue[(request.connid, request.msgid)] = request
        return CONTINUE_RESPONSE

    def do_modrdn(self, request):
        """
        MODRDN
        """
        if self.is_temporary_dn(request):
            return CONTINUE_RESPONSE
        self._log(logging.DEBUG, "do_modrdn = %s", request)
        self.req_queue[(request.connid, request.msgid)] = request
        return CONTINUE_RESPONSE

    def do_search(self, request):
        """
        SEARCH
        """
        _ = (self, request)  # pylint dummy
        return CONTINUE_RESPONSE

    def do_unbind(self, request):
        """
        UNBIND
        """
        _ = (self, request)  # pylint dummy
        return ""

    def do_result(self, request):
        """
        RESULT
        """
        _ = (self, request)  # pylint dummy
        try:
            original_request = self.req_queue.pop((request.connid, request.msgid))
        except KeyError:
            return ""
        self._log(logging.DEBUG, "do_result = %s", request)
        self._log(logging.INFO, "dn = %s", original_request.dn)
        self._log(logging.INFO, "reqtype = %s", original_request.reqtype)
        if original_request.reqtype == "ADD":
            self._log(logging.INFO, "entry = %s", original_request.entry)
        elif original_request.reqtype == "MODIFY":
            self._log(logging.INFO, "modops = %s", original_request.modops)
        if request.code == 0:
            self._log(logging.INFO, "binddn = %s", original_request.binddn)
            self._log(logging.INFO, "Call NATS for dn = %s", original_request.dn)
        else:
            self._log(logging.INFO, "code = %s", request.code)
        return ""

    def do_entry(self, request):
        """
        ENTRY
        """
        _ = (self, request)  # pylint dummy
        self._log(logging.DEBUG, "do_entry = %s", request)
        return ""

    def do_extended(self, request):
        """
        EXTERNAL
        """
        _ = (self, request)  # pylint dummy
        return CONTINUE_RESPONSE


if __name__ == "__main__":
    stdout_handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.INFO)

    ldap_base = os.environ["ldap_base"]

    ldaphandler = LDAPHandler(ldap_base)
    with SlapdSockServer(
        server_address="/sockoverlay-listener",
        handler_class=ldaphandler,
        logger=logger,
        average_count=10,
        socket_timeout=30,
        socket_permissions="600",
        allowed_uids=(0,),
        allowed_gids=(0,),
        thread_pool_size=PARALLEL_REQUESTS_MAX,
    ) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
