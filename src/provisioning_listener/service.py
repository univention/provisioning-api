# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from datetime import datetime
import logging

from provisioning_listener.port import LDAPProducerPort
from shared.models.queue import LDAP_STREAM, LDAP_SUBJECT, Message, PublisherName

logger = logging.getLogger(__name__)


async def ensure_stream():
    async with LDAPProducerPort() as ldap_port:
        await ldap_port.ensure_stream(LDAP_STREAM, [LDAP_SUBJECT])


async def handle_changes(new, old):
    message = Message(
        publisher_name=PublisherName.udm_listener,
        ts=datetime.now(),
        realm="ldap",
        topic="ldap",
        body={"new": new, "old": old},
    )

    async with LDAPProducerPort() as ldap_port:
        await ldap_port.add_message(LDAP_STREAM, LDAP_SUBJECT, message)
