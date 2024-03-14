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
    nats_host: str
    # Nats: port
    nats_port: int

    @property
    def nats_server(self) -> str:
        return f"nats://{self.nats_host}:{self.nats_port}"

    # Internal REST API: host
    internal_api_host: str
    # Internal REST API: port
    internal_api_port: int

    @property
    def internal_api_url(self) -> str:
        return f"http://{self.internal_api_host}:{self.internal_api_port}/internal/v1"


settings = Settings()
