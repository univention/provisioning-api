# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import pytest
from udm_transformer.port import UDMTransformerPort
from udm_transformer.service.udm import UDMMessagingService

failed_obj = {
    "cn": [b"selfserviceregistrationtemplate"],
    "displayName": [b"<firstname> <lastname><:strip>"],
    "homeDirectory": [b"/home/<username>"],
    "loginShell": [b"/bin/bash"],
    "userPrimaryGroupPreset": [
        b"cn=Domain Users,cn=groups,dc=univention-organization,dc=intranet"
    ],
    "objectClass": [b"univentionUserTemplate", b"univentionObject", b"top"],
    "univentionObjectType": [b"settings/usertemplate"],
    "structuralObjectClass": [b"univentionUserTemplate"],
    "entryUUID": [b"5db4db90-ccd0-103e-8b97-ed540dd2df8e"],
    "creatorsName": [b"cn=admin,dc=univention-organization,dc=intranet"],
    "createTimestamp": [b"20240702150612Z"],
    "entryCSN": [b"20240702150612.845806Z#000000#015#000000"],
    "modifiersName": [b"cn=admin,dc=univention-organization,dc=intranet"],
    "modifyTimestamp": [b"20240702150612Z"],
    "entryDN": [
        b"cn=selfserviceregistrationtemplate,cn=templates,cn=univention,dc=univention-organization,dc=intranet"
    ],
    "subschemaSubentry": [b"cn=Subschema"],
    "hasSubordinates": [b"FALSE"],
}


@pytest.mark.anyio
class TestUDMMessagingService:
    async def test_ldap_to_udm(self):
        udm_messaging_service = UDMMessagingService(UDMTransformerPort())
        udm_obj = udm_messaging_service.ldap_to_udm(failed_obj)
        assert udm_obj is None
