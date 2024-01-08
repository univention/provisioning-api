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
    # Nats: port
    nats_port: int = 4222

    # UDM REST API: base url
    udm_url: str = "http://localhost:8000/univention/udm"
    # UDM REST API: username
    udm_username: str = "Administrator"
    # UDM REST API: password
    udm_password: str = "univention"

    # Event REST API: base url
    event_url: str = "http://localhost:7777/events/v1"
    # Event REST API: username
    event_username: str = ""
    # Event REST API: password
    event_password: str = ""

    # LDAP : port
    ldap_port: int = 389
    # LDAP : host
    ldap_host: str = "localhost"
    # LDAP : server_uri
    ldap_server_uri: str = f"ldap://{ldap_host}:{ldap_port}"
    # LDAP : start_tls
    ldap_start_tls: int = 0
    # LDAP : base_dn
    ldap_base_dn: str = "dc=univention-organization,dc=intranet"
    # LDAP : host_dn
    ldap_host_dn: str = "cn=admin,dc=univention-organization,dc=intranet"
    # LDAP : password
    ldap_password: str = "univention"


settings = Settings()
