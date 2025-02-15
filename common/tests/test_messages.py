# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import pytest

from univention.provisioning.models.message import EmptyBodyError, Message, NoUDMTypeError


def test_empty_body_error():
    data = {
        "publisher_name": "udm-listener",
        "ts": "2025-02-15T11:18:06.309582",
        "realm": "ldap",
        "topic": "ldap",
        "body": {
            "new": None,
            "old": None,
        },
    }
    with pytest.raises(EmptyBodyError) as err:
        Message.model_validate(data)

    assert err


def test_no_udm_type_error():
    data = {
        "publisher_name": "udm-listener",
        "ts": "2025-02-15T11:18:06.309582",
        "realm": "ldap",
        "topic": "ldap",
        "body": {
            "new": {
                "objectClass": [b"top", b"person"],
                "cn": [b"admin"],
                "sn": [b"admin"],
                "userPassword": [b"{crypt}FYoR.QlE61o.QYi5VhscMRCU"],
                "structuralObjectClass": [b"person"],
                "entryUUID": [b"32174a46-7fda-103f-9691-ff75bd2a30b8"],
                "creatorsName": [b"cn=admin,dc=univention-organization,dc=intranet"],
                "createTimestamp": [b"20250215111732Z"],
                "entryCSN": [b"20250215111732.775650Z#000000#000#000000"],
                "modifiersName": [b"cn=admin,dc=univention-organization,dc=intranet"],
                "modifyTimestamp": [b"20250215111732Z"],
                "entryDN": [b"cn=admin,dc=univention-organization,dc=intranet"],
                "subschemaSubentry": [b"cn=Subschema"],
                "hasSubordinates": [b"FALSE"],
            },
            "old": None,
        },
    }
    with pytest.raises(NoUDMTypeError) as err:
        Message.model_validate(data)

    assert err
