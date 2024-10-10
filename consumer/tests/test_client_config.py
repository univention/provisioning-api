# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import pytest

from univention.provisioning.consumer.config import ProvisioningConsumerClientSettings

env_api_url = "PROVISIONING_API_BASE_URL"
env_username = "PROVISIONING_API_USERNAME"
env_password = "PROVISIONING_API_PASSWORD"


def test_consumer_name(monkeypatch):
    monkeypatch.delenv(env_username)
    with pytest.raises(ValueError):
        ProvisioningConsumerClientSettings()

    monkeypatch.setenv(env_username, "test-consumer")
    settings = ProvisioningConsumerClientSettings()
    assert settings.provisioning_api_username == "test-consumer"


def test_consumer_password(monkeypatch):
    monkeypatch.delenv(env_password)
    with pytest.raises(ValueError):
        ProvisioningConsumerClientSettings()

    monkeypatch.setenv(env_password, "test-consumer")
    settings = ProvisioningConsumerClientSettings()
    assert settings.provisioning_api_password == "test-consumer"


def test_base_url(monkeypatch):
    settings = ProvisioningConsumerClientSettings()
    assert settings.provisioning_api_base_url == "http://localhost:7777"

    monkeypatch.delenv(env_api_url)
    with pytest.raises(ValueError):
        ProvisioningConsumerClientSettings()

    monkeypatch.setenv(env_api_url, "http://testhost:1234")
    settings = ProvisioningConsumerClientSettings()
    assert settings.provisioning_api_base_url == "http://testhost:1234"


def test_property_consumer_registration_url():
    settings = ProvisioningConsumerClientSettings()
    assert settings.subscriptions_url == "http://localhost:7777/v1/subscriptions"


def test_property_consumer_messages_url(monkeypatch):
    monkeypatch.setenv(env_api_url, "http://foobar:5678")
    settings = ProvisioningConsumerClientSettings()
    assert settings.messages_url == "http://foobar:5678/v1/messages"
