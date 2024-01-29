# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import pytest


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


"""
- The UDM listener is triggered with an LDAP change event
- It will enrich its LDAP object with UDM data for it to become a UDM object
- UDM needs to be mocked
"""


@pytest.mark.xfail()
def test_udm_listener_enriches_ldap_object():
    raise NotImplementedError
