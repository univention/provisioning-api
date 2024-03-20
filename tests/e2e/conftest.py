# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import uuid

import pytest

from univention.admin.rest.client import UDM
from tests.conftest import REALMS_TOPICS

import shared.client  # noqa: E402

from typing import AsyncGenerator, Any, NamedTuple


class E2ETestSettings(NamedTuple):
    provisioning_api_base_url: str
    provisioning_admin_username: str
    provisioning_admin_password: str

    provisioning_events_username: str
    provisioning_events_password: str

    ldap_server_uri: str
    ldap_bind_dn: str
    ldap_bind_password: str

    udm_rest_api_base_url: str
    udm_rest_api_username: str
    udm_rest_api_password: str


def get_default_settings() -> E2ETestSettings:
    return E2ETestSettings(
        provisioning_api_base_url="http://localhost:7777",
        provisioning_admin_username="admin",
        provisioning_admin_password="provisioning",
        provisioning_events_username="udm",
        provisioning_events_password="udmpass",
        ldap_server_uri="ldap://localhost:3890",
        ldap_bind_dn="cn=admin,dc=univention-organization,dc=intranet",
        ldap_bind_password="univention",
        udm_rest_api_base_url="http://localhost:8000/univention/udm/",
        udm_rest_api_username="cn=admin",
        udm_rest_api_password="univention",
    )


def get_pipeline_settings() -> E2ETestSettings:
    return get_default_settings()._replace(
        provisioning_api_base_url="http://events-and-consumer-api:7777/",
        ldap_server_uri="ldap://ldap-server:389",
        udm_rest_api_base_url="http://udm-rest-api:9979/udm/",
    )


def get_gaia_settings() -> E2ETestSettings:
    return get_default_settings()._replace(
        provisioning_admin_username="admin",
        provisioning_admin_password="9f42908c164a41d2771b4451397f68ae3c13a220",
        provisioning_events_username="udmproducer",
        provisioning_events_password="05c19490698eb7294776565f70e88abcca183499",
        ldap_bind_dn="cn=admin,dc=swp-ldap,dc=internal",
        ldap_bind_password="e958ec347ebf4cd1959f4e8536dcedfc3fcea023",
        # Test if it also works with external url instead of port-forward
        udm_rest_api_base_url="http://localhost:9979/udm/",
        udm_rest_api_username="cn=admin",
        udm_rest_api_password="e958ec347ebf4cd1959f4e8536dcedfc3fcea023",
    )


TEST_SETTINGS = {
    "local": get_default_settings,
    "pipeline": get_pipeline_settings,
    "gaia": get_gaia_settings,
}


SUBSCRIBER_NAME = str(uuid.uuid4())
SUBSCRIBER_PASSWORD = "subscriberpassword"


def pytest_addoption(parser):
    # Portal tests options
    parser.addoption(
        "--environment",
        default="local",
        help=(
            "set the environment you are running the tests in."
            "accepted values are: 'local', 'dev-env', 'pipeline' and 'gaia'"
        ),
    )


@pytest.fixture(scope="session")
def test_settings(pytestconfig) -> E2ETestSettings:
    test_settings = TEST_SETTINGS.get(pytestconfig.option.environment)
    assert test_settings, "invalid value for --environment"
    return test_settings()


@pytest.fixture
def udm(test_settings: E2ETestSettings) -> UDM:
    udm = UDM(
        test_settings.udm_rest_api_base_url,
        test_settings.udm_rest_api_username,
        test_settings.udm_rest_api_password,
    )
    # test the connection
    udm.get_ldap_base()
    return udm


@pytest.fixture
def client_settings(test_settings: E2ETestSettings) -> shared.client.Settings:
    return shared.client.Settings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        provisioning_api_username=SUBSCRIBER_NAME,
        provisioning_api_password=SUBSCRIBER_PASSWORD,
    )


@pytest.fixture
def admin_client_settings(test_settings: E2ETestSettings) -> shared.client.Settings:
    return shared.client.Settings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        provisioning_api_username=test_settings.provisioning_admin_username,
        provisioning_api_password=test_settings.provisioning_admin_password,
    )


@pytest.fixture
async def provisioning_client(
    client_settings,
) -> AsyncGenerator[shared.client.AsyncClient, Any]:
    async with shared.client.AsyncClient(client_settings) as client:
        yield client


@pytest.fixture
async def provisioning_admin_client(
    admin_client_settings,
) -> AsyncGenerator[shared.client.AsyncClient, Any]:
    async with shared.client.AsyncClient(admin_client_settings) as client:
        yield client


@pytest.fixture
async def simple_subscription(
    provisioning_admin_client: shared.client.AsyncClient,
    provisioning_client: shared.client.AsyncClient,
) -> AsyncGenerator[str, Any]:
    await provisioning_admin_client.create_subscription(
        name=SUBSCRIBER_NAME,
        realms_topics=REALMS_TOPICS,
        password=SUBSCRIBER_PASSWORD,
        request_prefill=False,
    )

    yield SUBSCRIBER_NAME

    await provisioning_client.cancel_subscription(SUBSCRIBER_NAME)
