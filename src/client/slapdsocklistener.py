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

from binascii import a2b_base64
import logging
import os
from queue import Queue
import sys

from slapdsock.service import SlapdSockServer
from slapdsock.handler import SlapdSockHandler
from slapdsock.message import CONTINUE_RESPONSE
from ldap0.res import decode_response_ctrls
from ldap0.controls.readentry import PostReadControl, PreReadControl

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

    def __init__(self, ldap_base, ldap_threads):
        self.req_queue = Queue(maxsize=ldap_threads)
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
        self.req_queue.put((request.connid, request.msgid), block=True)
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
        self.req_queue.put((request.connid, request.msgid), block=True)
        return CONTINUE_RESPONSE

    def do_modify(self, request):
        """
        MODIFY
        """
        if self.is_temporary_dn(request):
            return CONTINUE_RESPONSE
        self._log(logging.DEBUG, "do_modify = %s", request)
        self.req_queue.put((request.connid, request.msgid), block=True)
        return CONTINUE_RESPONSE

    def do_modrdn(self, request):
        """
        MODRDN
        """
        if self.is_temporary_dn(request):
            return CONTINUE_RESPONSE
        self._log(logging.DEBUG, "do_modrdn = %s", request)
        self.req_queue.put((request.connid, request.msgid), block=True)
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
        if getattr(request, "dn", None) is None:
            # A search result or anything where RESULTRequest._parse_ldif didn't find anything.
            return ""
        self._log(logging.DEBUG, "do_result = %s", request)
        if self.is_temporary_dn(request):
            self._log(logging.INFO, "ignoring dn = %s", request.dn)
            return ""
        self._log(logging.INFO, "dn = %s", request.dn)
        if request.parsed_ldif:
            self._log(logging.DEBUG, "parsed_ldif = %s", request.parsed_ldif)
            if isinstance(request.parsed_ldif, list):
                reqtype = "MODIFY"
            elif b"newrdn" in request.parsed_ldif:
                reqtype = "MODRDN"
            else:
                reqtype = "ADD"
        elif request.parsed_ldif is None:
            reqtype = "DELETE"

        self._log(logging.DEBUG, "reqtype = %s", reqtype)
        self._log(logging.DEBUG, "parsed_ldif = %s", request.parsed_ldif)
        if request.code == 0:
            self._log(logging.INFO, "binddn = %s", request.binddn)
            self._log(logging.DEBUG, "ctrls = %s", request.ctrls)
            ctrls = [
                (control_type, criticality, a2b_base64(control_value))
                for (control_type, criticality, control_value) in request.ctrls
            ]
            ctrls = decode_response_ctrls(ctrls)
            for ctrl in ctrls:
                if isinstance(ctrl, PostReadControl):
                    self._log(logging.INFO, "PostRead entry_as = %s", ctrl.res.entry_as)
                elif isinstance(ctrl, PreReadControl):
                    self._log(logging.INFO, "PreRead entry_as = %s", ctrl.res.entry_as)
            self._log(logging.INFO, "Call NATS for %s operation on dn = %s" % (reqtype, request.dn))
        else:
            self._log(logging.INFO, "ignoring op with RESULT code = %s", request.code)
        self.req_queue.get()  # signal one seat is free
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


def main():
    stdout_handler = logging.StreamHandler(sys.stdout)
    logger = logging.getLogger()
    logger.addHandler(stdout_handler)
    logger.setLevel(logging.INFO)

    ldap_base = os.environ["ldap_base"]
    ldap_threads = os.environ["ldap_threads"]

    ldaphandler = LDAPHandler(ldap_base, ldap_threads)
    with SlapdSockServer(
        server_address="/var/lib/univention-ldap/slapd-sock",
        handler_class=ldaphandler,
        logger=logger,
        average_count=10,
        socket_timeout=30,
        socket_permissions="600",
        allowed_uids=(0,),
        allowed_gids=(0,),
        thread_pool_size=ldap_threads,
    ) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()


if __name__ == "__main__":
    main()
