# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import os

from shared.client.config import ClientSettings


env_consumer_name = "CONSUMER_NAME"
env_realms_topics = "REALMS_TOPICS"


def _clear_env_vars(env_vars: [str]):
    for env_var in env_vars:
        if env_var in os.environ:
            os.environ.pop(env_var)


def test_consumer_name():
    _clear_env_vars([env_consumer_name])
    settings = ClientSettings()

    assert len(settings.consumer_name.split("-")) == 5

    os.environ[env_consumer_name] = "test-consumer"
    settings = ClientSettings()

    assert settings.consumer_name == "test-consumer"
    _clear_env_vars([env_consumer_name])


def test_realms_topics():
    _clear_env_vars([env_realms_topics])
    settings = ClientSettings()
    assert settings.realms_topics == []

    os.environ[env_realms_topics] = '[["udm", "users/user"]]'
    settings = ClientSettings()
    assert settings.realms_topics == [("udm", "users/user")]
    _clear_env_vars([env_realms_topics])


def test_property_consumer_registration_url():
    settings = ClientSettings()
    assert (
        settings.consumer_registration_url == "http://localhost:7777/subscriptions/v1"
    )


def test_property_consumer_messages_url():
    settings = ClientSettings()
    assert settings.consumer_messages_url == "http://localhost:7777/messages/v1"
