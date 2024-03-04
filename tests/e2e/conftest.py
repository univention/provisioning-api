# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import AsyncGenerator
import uuid

import pytest

from univention.admin.rest.client import UDM
import shared.client  # noqa: E402
from shared.client.config import ClientSettings
from tests.conftest import REALMS_TOPICS
from tests import set_test_env_vars

set_test_env_vars()


def pytest_addoption(parser):
    # Portal tests options
    parser.addoption(
        "--provisioning-base-url",
        default="http://localhost:7777/",
        help="Base URL of the provisioning API",
    )
    parser.addoption(
        "--udm-rest-api-base-url",
        default="http://localhost:9979/udm/",
        help="Base URL of the UDM REST API",
    )
    parser.addoption(
        "--ldap-server-base-url",
        default="ldap://localhost:389",
        help="Base URL of the LDAP server/",
    )
    parser.addoption(
        "--udm-admin-username", default="cn=admin", help="UDM admin login password"
    )
    parser.addoption(
        "--udm-admin-password", default="univention", help="UDM admin login password"
    )


@pytest.fixture(scope="session")
def provisioning_base_url(pytestconfig) -> str:
    return pytestconfig.option.provisioning_base_url.rstrip("/")


@pytest.fixture(scope="session")
def ldap_server_base_url(pytestconfig) -> str:
    return pytestconfig.option.ldap_server_base_url.rstrip("/")


@pytest.fixture(scope="session")
def udm_admin_username(pytestconfig) -> str:
    return pytestconfig.option.udm_admin_username


@pytest.fixture(scope="session")
def udm_admin_password(pytestconfig) -> str:
    return pytestconfig.option.udm_admin_password


@pytest.fixture(scope="session")
def udm_rest_api_base_url(pytestconfig) -> str:
    """Base URL to reach the UDM Rest API."""
    return pytestconfig.option.udm_rest_api_base_url.rstrip("/") + "/"


@pytest.fixture
def udm(udm_rest_api_base_url, udm_admin_username, udm_admin_password) -> UDM:
    udm = UDM(udm_rest_api_base_url, udm_admin_username, udm_admin_password)
    # test the connection
    udm.get_ldap_base()
    return udm


@pytest.fixture
async def provisioning_client(
    provisioning_base_url,
) -> AsyncGenerator[shared.client.AsyncClient, None]:
    provisioning_client = shared.client.AsyncClient(
        ClientSettings(
            consumer_name=str(uuid.uuid4()),
            realms_topics=REALMS_TOPICS,
            request_prefill=False,
            provisioning_api_url=provisioning_base_url,
            provisioning_api_password="",
        )
    )

    await provisioning_client.create_subscription()

    yield provisioning_client

    await provisioning_client.cancel_subscription()
