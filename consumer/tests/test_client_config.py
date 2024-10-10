# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import os

from univention.provisioning.consumer.config import ProvisioningConsumerClientSettings

env_api_url = "PROVISIONING_API_BASE_URL"
env_username = "PROVISIONING_API_USERNAME"
env_password = "PROVISIONING_API_PASSWORD"


def _clear_env_vars(env_vars: list[str]):
    for env_var in env_vars:
        if env_var in os.environ:
            os.environ.pop(env_var)


def test_consumer_name():
    _clear_env_vars([env_username])
    settings = ProvisioningConsumerClientSettings()

    os.environ[env_username] = "test-consumer"
    settings = ProvisioningConsumerClientSettings()

    assert settings.provisioning_api_username == "test-consumer"
    _clear_env_vars([env_username])


def test_consumer_password():
    _clear_env_vars([env_password])
    settings = ProvisioningConsumerClientSettings()

    os.environ[env_password] = "test-consumer"
    settings = ProvisioningConsumerClientSettings()

    assert settings.provisioning_api_password == "test-consumer"
    _clear_env_vars([env_password])


def test_base_url():
    _clear_env_vars([env_api_url])
    settings = ProvisioningConsumerClientSettings()

    assert settings.provisioning_api_base_url == "http://localhost:7777"

    os.environ[env_api_url] = "http://testhost:1234"
    settings = ProvisioningConsumerClientSettings()

    assert settings.provisioning_api_base_url == "http://testhost:1234"
    _clear_env_vars([env_api_url])


def test_property_consumer_registration_url():
    settings = ProvisioningConsumerClientSettings()
    assert settings.subscriptions_url == "http://localhost:7777/v1/subscriptions"


def test_property_consumer_messages_url():
    os.environ[env_api_url] = "http://foobar:5678"
    settings = ProvisioningConsumerClientSettings()
    assert settings.messages_url == "http://foobar:5678/v1/messages"
