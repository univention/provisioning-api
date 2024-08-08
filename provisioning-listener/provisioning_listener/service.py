# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from datetime import datetime
from typing import Any, Dict

from univention.provisioning.models.queue import (
    LDAP_STREAM,
    LDAP_SUBJECT,
    Body,
    Message,
    PublisherName,
)

from provisioning_listener.port import LDAPProducerPort

logger = logging.getLogger(__name__)


async def ensure_stream():
    async with LDAPProducerPort() as ldap_port:
        await ldap_port.ensure_stream(LDAP_STREAM, False, [LDAP_SUBJECT])


async def handle_changes(new: Dict[str, Any], old: Dict[str, Any]):
    message = Message(
        publisher_name=PublisherName.ldif_producer,
        ts=datetime.now(),
        realm="ldap",
        topic="ldap",
        body=Body(new=new, old=old),
    )

    async with LDAPProducerPort() as ldap_port:
        await ldap_port.add_message(LDAP_STREAM, LDAP_SUBJECT, message)
