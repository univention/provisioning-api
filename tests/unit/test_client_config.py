# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import os

from shared.client.config import Settings


env_consumer_name = "CONSUMER_NAME"
env_api_host = "PROVISIONING_API_HOST"
env_api_port = "PROVISIONING_API_PORT"
env_realms_topics = "REALMS_TOPICS"


def _clear_env_vars(env_vars: [str]):
    for env_var in env_vars:
        if env_var in os.environ:
            os.environ.pop(env_var)


def test_consumer_name():
    _clear_env_vars([env_consumer_name])
    settings = Settings()

    assert len(settings.consumer_name.split("-")) == 5

    os.environ[env_consumer_name] = "test-consumer"
    settings = Settings()

    assert settings.consumer_name == "test-consumer"
    _clear_env_vars([env_consumer_name])


def test_property_base_url():
    _clear_env_vars([env_api_host, env_api_port])
    settings = Settings()

    assert settings.base_url == "http://localhost:7777"

    os.environ[env_api_host] = "testhost"
    settings = Settings()

    assert settings.base_url == "http://testhost:7777"

    os.environ[env_api_port] = "1234"
    settings = Settings()

    assert settings.base_url == "http://testhost:1234"
    _clear_env_vars([env_api_host, env_api_port])


def test_realms_topics():
    _clear_env_vars([env_realms_topics])
    settings = Settings()
    assert settings.realms_topics == []

    os.environ[env_realms_topics] = '[["udm", "users/user"]]'
    settings = Settings()
    assert settings.realms_topics == [("udm", "users/user")]
    _clear_env_vars([env_realms_topics])


def test_property_consumer_registration_url():
    settings = Settings()
    assert (
        settings.consumer_registration_url == "http://localhost:7777/subscriptions/v1"
    )


def test_property_consumer_messages_url():
    settings = Settings()
    assert settings.consumer_messages_url == "http://localhost:7777/messages/v1"
