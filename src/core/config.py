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

    # Redis: host
    redis_host: str = "localhost"
    # Redis: port
    redis_port: int = 6379

    # Nats: host
    nats_host: str = "localhost"
    # Redis: port
    nats_port: int = 4222

    # UDM REST API: base url
    udm_url: str = "http://localhost:8000/univention/udm"
    # UDM REST API: username
    udm_username: str = "Administrator"
    # UDM REST API: password
    udm_password: str = "univention"


settings = Settings()
