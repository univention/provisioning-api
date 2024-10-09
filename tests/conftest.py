# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import pytest

from univention.provisioning.rest.main import app
from univention.provisioning.rest.port import Port

# from server.core.app.dependencies import AppSettingsDep
from .mocks import port_fake_dependency

# from unittest.mock import AsyncMock, patch
# from .mock_data import CREDENTIALS
# from . import ENV_DEFAULTS


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"


# def settings_mock() -> AsyncMock:
#     settings = patch("server.core.app.config.app_settings").start()
#     settings.admin_username = ENV_DEFAULTS["admin_username"]
#     settings.admin_password = ENV_DEFAULTS["admin_password"]
#     settings.events_username_udm = ENV_DEFAULTS["events_username_udm"]
#     settings.events_password_udm = ENV_DEFAULTS["events_password_udm"]
#     return settings


@pytest.fixture(autouse=True)
def override_dependencies():
    # Override original port
    # app.dependency_overrides[AppSettingsDep] = settings_mock
    app.dependency_overrides[Port.port_dependency] = port_fake_dependency
    yield  # This will ensure the setup is done before tests and cleanup after
    # Clear the overrides after the tests
    app.dependency_overrides.clear()
