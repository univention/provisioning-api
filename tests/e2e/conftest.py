# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import pytest
from univention.admin.rest.client import UDM

import shared.client
from tests.conftest import REALMS_TOPICS


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
def provisioning_base_url(pytestconfig) -> str:
    return pytestconfig.option.provisioning_api_base_url


@pytest.fixture(scope="session")
def udm_admin_username(pytestconfig) -> str:
    return pytestconfig.option.udm_admin_username


@pytest.fixture(scope="session")
def udm_admin_password(pytestconfig) -> str:
    return pytestconfig.option.udm_admin_password


@pytest.fixture(scope="session")
def udm_rest_api_base_url(pytestconfig) -> str:
    """Base URL to reach the UDM Rest API."""
    return pytestconfig.getoption("--udm-rest-api-base-url")


@pytest.fixture
def udm(udm_rest_api_base_url, udm_admin_username, udm_admin_password) -> UDM:
    udm = UDM(udm_rest_api_base_url, udm_admin_username, udm_admin_password)
    # test the connection
    udm.get_ldap_base()
    return udm


@pytest.fixture
def provisioning_client(provisioning_base_url) -> shared.client.AsyncClient:
    return shared.client.AsyncClient()


@pytest.fixture
async def simple_subscription(provisioning_client: shared.client.AsyncClient) -> str:
    subscriber_name = str(uuid.uuid4())
    await provisioning_client.create_subscription(
        name=subscriber_name,
        realms_topics=REALMS_TOPICS,
        request_prefill=False,
    )

    yield subscriber_name

    await provisioning_client.cancel_subscription(subscriber_name)
