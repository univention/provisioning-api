# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import json
import uuid
from typing import AsyncGenerator, Any, NamedTuple
from univention.admin.rest.client import UDM
from tests.conftest import REALMS_TOPICS
from univention.provisioning.consumer import AsyncClient, Settings
import pytest


class E2ETestSettings(NamedTuple):
    provisioning_api_base_url: str
    provisioning_admin_username: str
    provisioning_admin_password: str

    provisioning_events_username: str
    provisioning_events_password: str

    ldap_server_uri: str
    ldap_base: str
    ldap_bind_dn: str
    ldap_bind_password: str

    udm_rest_api_base_url: str
    udm_rest_api_username: str
    udm_rest_api_password: str


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
    environment = pytestconfig.option.environment
    assert environment in (
        "local",
        "dev-env",
        "pipeline",
        "gaia",
    ), "invalid value for --environment"

    with open("./tests/e2e/e2e_settings.json") as f:
        json_settings = json.load(f)

    settings = E2ETestSettings(**json_settings["local"])
    if environment == "local":
        return settings

    return settings._replace(**json_settings[environment])


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
def subscriber_name() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def subscriber_password() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def client_settings(
    test_settings: E2ETestSettings, subscriber_name, subscriber_password
) -> Settings:
    return Settings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        provisioning_api_username=subscriber_name,
        provisioning_api_password=subscriber_password,
    )


@pytest.fixture
def admin_client_settings(test_settings: E2ETestSettings) -> Settings:
    return Settings(
        provisioning_api_base_url=test_settings.provisioning_api_base_url,
        provisioning_api_username=test_settings.provisioning_admin_username,
        provisioning_api_password=test_settings.provisioning_admin_password,
    )


@pytest.fixture
async def provisioning_client(
    client_settings,
) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(client_settings) as client:
        yield client


@pytest.fixture
async def provisioning_admin_client(
    admin_client_settings,
) -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(admin_client_settings) as client:
        yield client


@pytest.fixture
async def simple_subscription(
    subscriber_name,
    subscriber_password,
    provisioning_admin_client: AsyncClient,
) -> AsyncGenerator[str, Any]:
    await provisioning_admin_client.create_subscription(
        name=subscriber_name,
        password=subscriber_password,
        realms_topics=REALMS_TOPICS,
        request_prefill=False,
    )

    yield subscriber_name

    await provisioning_admin_client.cancel_subscription(subscriber_name)
