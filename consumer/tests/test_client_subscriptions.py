# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import logging

from pytest_httpserver import HTTPServer

from univention.provisioning.consumer.api import ProvisioningConsumerClient
from univention.provisioning.consumer.config import ProvisioningConsumerClientSettings
from univention.provisioning.models.subscription import RealmTopic


def client_settings(httpserver: HTTPServer) -> ProvisioningConsumerClientSettings:
    return ProvisioningConsumerClientSettings(
        provisioning_api_base_url=httpserver.url_for("/"),
        provisioning_api_username="admin",
        provisioning_api_password="admin-password",
        log_level="DEBUG",
    )


async def test_create_subscription_does_not_log_the_password(httpserver: HTTPServer, caplog):
    httpserver.expect_request("/v1/subscriptions", method="POST").respond_with_data(status=201)
    caplog.set_level(logging.DEBUG, logger="univention.provisioning.consumer")

    async with ProvisioningConsumerClient(client_settings(httpserver)) as client:
        await client.create_subscription(
            name="portal-consumer",
            password="consumer-secret-pw",
            realms_topics=[RealmTopic(realm="udm", topic="users/user")],
        )

    assert "portal-consumer" in caplog.text
    assert "consumer-secret-pw" not in caplog.text
    assert httpserver.log[0][0].get_json()["password"] == "consumer-secret-pw"
