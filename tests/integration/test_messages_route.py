# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH


import httpx
import pytest

from univention.provisioning.rest.config import app_settings
from univention.provisioning.testing.mock_data import FLAT_MESSAGE


@pytest.mark.anyio
class TestInternalApi:
    settings = app_settings()

    async def test_add_event(self, client: httpx.AsyncClient):
        response = await client.post(
            "/v1/messages",
            json=FLAT_MESSAGE,
            auth=(self.settings.events_username_udm, self.settings.events_password_udm),
        )
        assert response.status_code == 202
