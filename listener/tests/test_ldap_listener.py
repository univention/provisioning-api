# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from unittest.mock import AsyncMock, patch

import msgpack
import pytest

from univention.provisioning.backends.nats_mq import LdapQueue
from univention.provisioning.listener.config import LdapProducerSettings
from univention.provisioning.listener.mq_adapter_nats import MessageQueueNatsAdapter, is_udm_message

user_entry = {
    "krb5MaxLife": [b"86400"],
    "krb5MaxRenew": [b"604800"],
    "uid": [b"juanpe"],
    "uidNumber": [b"2005"],
    "givenName": [b"juanp"],
    "homeDirectory": [b"/home/juanpe"],
    "loginShell": [b"/bin/bash"],
    "mailPrimaryAddress": [b"juanpe@univention-organization.test"],
    "mailForwardCopyToSelf": [b"0"],
    "opendeskFileshareEnabled": [b"TRUE"],
    "opendeskFileshareAdmin": [b"FALSE"],
    "opendeskProjectmanagementEnabled": [b"TRUE"],
    "opendeskProjectmanagementAdmin": [b"FALSE"],
    "opendeskKnowledgemanagementEnabled": [b"TRUE"],
    "opendeskLivecollaborationEnabled": [b"TRUE"],
    "isOxUser": [b"OK"],
    "oxAccess": [b"groupware"],
    "oxUserQuota": [b"-1"],
    "krb5PrincipalName": [b"juanpe@UNIVENTION-ORGANIZATION.INTRANET"],
    "krb5KDCFlags": [b"126"],
    "sambaBadPasswordCount": [b"0"],
    "sambaBadPasswordTime": [b"0"],
    "sambaAcctFlags": [b"[U          ]"],
    "objectClass": [
        b"univentionMail",
        b"top",
        b"posixAccount",
        b"opendeskLivecollaborationUser",
        b"oxUserObject",
        b"opendeskKnowledgemanagementUser",
        b"inetOrgPerson",
        b"univentionObject",
        b"automount",
        b"univentionPWHistory",
        b"krb5Principal",
        b"organizationalPerson",
        b"opendeskProjectmanagementUser",
        b"sambaSamAccount",
        b"shadowAccount",
        b"krb5KDCEntry",
        b"person",
        b"opendeskFileshareUser",
    ],
    "sambaSID": [b"S-1-5-21-UNSET-5010"],
    "gidNumber": [b"5001"],
    "sambaPrimaryGroupSID": [b"S-1-5-21-UNSET-513"],
    "univentionObjectType": [b"users/user"],
    "structuralObjectClass": [b"inetOrgPerson"],
    "entryUUID": [b"90f2821e-9ff3-103e-8c17-67ac117796a0"],
    "creatorsName": [b"uid=default.admin,cn=users,dc=univention-organization,dc=intranet"],
    "createTimestamp": [b"20240506125448Z"],
    "memberOf": [
        b"cn=managed-by-attribute-Groupware,cn=groups,dc=univention-organization,dc=intranet",
        b"cn=managed-by-attribute-Fileshare,cn=groups,dc=univention-organization,dc=intranet",
        b"cn=managed-by-attribute-Projectmanagement,cn=groups,dc=univention-organization,dc=intranet",
        b"cn=managed-by-attribute-Knowledgemanagement,cn=groups,dc=univention-organization,dc=intranet",
        b"cn=managed-by-attribute-Livecollaboration,cn=groups,dc=univention-organization,dc=intranet",
        b"cn=Domain Users,cn=groups,dc=univention-organization,dc=intranet",
    ],
    "sn": [b"garcia"],
    "oxDisplayName": [b"juanp garcia"],
    "cn": [b"juanp garcia"],
    "gecos": [b"juanp garcia"],
    "displayName": [b"juanp garcia"],
    "userPassword": [b"{BCRYPT}$2b$12$68J5r4b.6ILOUXBH34ZnP.eJB3YhgfO7Mj/jojGyB1KmX7vJR2N9y"],
    "krb5Key": [
        b'0`\xa1+0)\xa0\x03\x02\x01\x12\xa1"\x04 Whj|\x98R\xba}\xde\x02\xce5\x84\x97\x99\x93\xd0\xb2Xt=p\xad \xcc\xde\xb0o\xc2.\x92\xea\xa210/\xa0\x03\x02\x01\x03\xa1(\x04&UNIVENTION-ORGANIZATION.INTRANETjuanpe',  # noqa E501
        b"0P\xa1\x1b0\x19\xa0\x03\x02\x01\x11\xa1\x12\x04\x10W\xb7\x97\x9b`\xb4\xba\xd9d\xa3\xfb\x85\xd7\x9fb\xc5\xa210/\xa0\x03\x02\x01\x03\xa1(\x04&UNIVENTION-ORGANIZATION.INTRANETjuanpe",  # noqa E501
        b'0`\xa1+0)\xa0\x03\x02\x01\x14\xa1"\x04 =y\xf4\xaax]\xe9\xe0\xf6\x8e\xa0\x86\x9a]\x87\xb7\xab\x9ba7\xb5\x899jX\xb9\x9c\xc3\x9c\x02\xb7\xae\xa210/\xa0\x03\x02\x01\x03\xa1(\x04&UNIVENTION-ORGANIZATION.INTRANETjuanpe',  # noqa E501
        b"0P\xa1\x1b0\x19\xa0\x03\x02\x01\x13\xa1\x12\x04\x10\xfe\x83;\x05\x82\x00\xe1<x\xb4\x1f`\xffm\xe8\xef\xa210/\xa0\x03\x02\x01\x03\xa1(\x04&UNIVENTION-ORGANIZATION.INTRANETjuanpe",  # noqa E501
        b"0X\xa1#0!\xa0\x03\x02\x01\x10\xa1\x1a\x04\x18\xb9\x0e\xc7T\xf2I\xa7\xfba#\xc4R\x1fI\xa7z\xa8b \x13\x0b\xd3^d\xa210/\xa0\x03\x02\x01\x03\xa1(\x04&UNIVENTION-ORGANIZATION.INTRANETjuanpe",  # noqa E501
        b"0P\xa1\x1b0\x19\xa0\x03\x02\x01\x17\xa1\x12\x04\x10gD\xf5\x8d\xb8\x11\xd7[\x9c\xff\x9c\xd7\x05\x7f\x13\x1a\xa210/\xa0\x03\x02\x01\x03\xa1(\x04&UNIVENTION-ORGANIZATION.INTRANETjuanpe",  # noqa E501
    ],
    "krb5KeyVersionNumber": [b"2"],
    "pwhistory": [
        b"{BCRYPT}$2b$12$1g0sbXAHkFJF/OxXJYkZwOXSeIhT4TiUnHItjyA.KKgbIyJW/3kMO {BCRYPT}$2b$12$MBFS9ScBE5Oz1KkvGPIlOOMc2jO8vWk0.a/4/yWUku1qDT24FpPLq"  # noqa E501
    ],
    "sambaNTPassword": [b"6744F58DB811D75B9CFF9CD7057F131A"],
    "sambaPwdLastSet": [b"1715007637"],
    "entryCSN": [b"20240506150037.834049Z#000000#000#000000"],
    "modifiersName": [b"uid=default.admin,cn=users,dc=univention-organization,dc=intranet"],
    "modifyTimestamp": [b"20240506150037Z"],
    "entryDN": [b"uid=juanpe,cn=users,dc=univention-organization,dc=intranet"],
    "subschemaSubentry": [b"cn=Subschema"],
    "hasSubordinates": [b"FALSE"],
}


@pytest.fixture
def mock_settings():
    return LdapProducerSettings(
        nats_user="test_user",
        nats_password="test_password",
        nats_host="localhost",
        nats_port=4222,
        nats_max_reconnect_attempts=5,
        nats_retry_delay=10,
        nats_max_retry_count=3,
        terminate_listener_on_exception=False,
    )


@pytest.fixture
def mock_nats_mq():
    with patch("univention.provisioning.listener.mq_adapter_nats.NatsMessageQueue", autospec=True) as mock:
        adapter = mock.return_value
        adapter.connect = AsyncMock()
        adapter.close = AsyncMock()
        adapter.add_message = AsyncMock()
        adapter.ensure_stream = AsyncMock()
        yield adapter


def test_is_udm_message_with_new():
    new = {"univentionObjectType": [b"users/user"]}
    old = {}
    assert is_udm_message(new, old) is True


def test_is_udm_message_with_old():
    new = {}
    old = {"univentionObjectType": [b"users/user"]}
    assert is_udm_message(new, old) is True


def test_is_udm_message_without_type():
    new = {"someField": "value"}
    old = {}
    assert is_udm_message(new, old) is False


async def test_ensure_queue_exists(mock_settings, mock_nats_mq):
    async with MessageQueueNatsAdapter(mock_settings) as adapter:
        await adapter.ensure_queue_exists()

    mock_nats_mq.connect.assert_awaited_once()
    mock_nats_mq.ensure_stream.assert_awaited_once_with(LdapQueue())
    mock_nats_mq.close.assert_awaited_once()


async def test_enqueue_change_event(mock_settings, mock_nats_mq):
    async with MessageQueueNatsAdapter(mock_settings) as adapter:
        await adapter.enqueue_change_event(user_entry, {})

    mock_nats_mq.connect.assert_awaited_once()
    mock_nats_mq.add_message.assert_awaited_once()

    call_args = mock_nats_mq.add_message.call_args
    assert call_args[0][0] == LdapQueue()

    encoded_message = call_args[0][1]
    decoded = msgpack.unpackb(encoded_message)
    assert decoded["publisher_name"] == "ldif-producer"
    assert decoded["realm"] == "ldap"
    assert decoded["topic"] == "ldap"
    assert decoded["body"]["new"] == user_entry
    assert decoded["body"]["old"] == {}

    mock_nats_mq.close.assert_awaited_once()


async def test_enqueue_skips_non_udm_messages(mock_settings, mock_nats_mq):
    non_udm_entry = {"someField": "value"}

    async with MessageQueueNatsAdapter(mock_settings) as adapter:
        await adapter.enqueue_change_event(non_udm_entry, {})

    mock_nats_mq.connect.assert_awaited_once()
    mock_nats_mq.add_message.assert_not_awaited()
    mock_nats_mq.close.assert_awaited_once()
