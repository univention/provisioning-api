# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# from _pytest.fixtures import pytestconfig

import pytest

from univention.admin.rest.client import UDM


def pytest_addoption(parser):
    # Portal tests options
    parser.addoption(
        "--provisioning-api-base-url",
        default="http://localhost:7777/",
        help="Base URL of the UDM REST API",
    )
    parser.addoption(
        "--udm-rest-api-base-url",
        default="http://localhost:9979/udm/",
        help="Base URL of the UDM REST API",
    )
    parser.addoption(
        "--udm-admin-username", default="cn=admin", help="UDM admin login password"
    )
    parser.addoption(
        "--udm-admin-password", default="univention", help="UDM admin login password"
    )


@pytest.fixture(scope="session")
def udm_admin_username(pytestconfig):
    return pytestconfig.option.udm_admin_username


@pytest.fixture(scope="session")
def udm_admin_password(pytestconfig):
    return pytestconfig.option.udm_admin_password


@pytest.fixture(scope="session")
def udm_rest_api_base_url(pytestconfig):
    """Base URL to reach the UDM Rest API."""
    return pytestconfig.getoption("--udm-rest-api-base-url")


@pytest.fixture
def udm(udm_rest_api_base_url, udm_admin_username, udm_admin_password) -> UDM:
    udm = UDM(udm_rest_api_base_url, udm_admin_username, udm_admin_password)
    # test the connection
    udm.get_ldap_base()
    return udm
