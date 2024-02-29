# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Python log level
    log_level: str = "INFO"

    # FastAPI: debug mode
    debug: bool = True
    # FastAPI: webserver root path
    root_path: str = ""
    # FastAPI: disable CORS checks
    cors_all: bool = False

    # Nats: host
    nats_host: str = "localhost"
    # Nats: port
    nats_port: int = 4222

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"

    # Consumer and Event REST API: host
    consumer_event_host: str = "localhost"
    # Consumer and Event REST API: port
    consumer_event_port: int = 7777
    # Consumer and Event REST API: username
    consumer_event_username: str = ""
    # Consumer and Event REST API: password
    consumer_event_password: str = ""

    @property
    def event_url(self) -> str:
        return f"http://{self.consumer_event_host}:{self.consumer_event_port}/events/v1"

    @property
    def consumer_registration_url(self) -> str:
        return f"http://{self.consumer_event_host}:{self.consumer_event_port}/subscriptions/v1"

    @property
    def consumer_messages_url(self) -> str:
        return (
            f"http://{self.consumer_event_host}:{self.consumer_event_port}/messages/v1"
        )


settings = Settings()
