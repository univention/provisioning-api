# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH
from typing import NamedTuple
from urllib.parse import urljoin


class E2ETestSettings(NamedTuple):
    provisioning_api_base_url_primary: str
    provisioning_api_base_url: str
    provisioning_admin_username: str
    provisioning_admin_password: str

    provisioning_events_username: str
    provisioning_events_password: str

    nats_url_primary: str
    nats_url: str
    nats_user: str
    nats_password: str

    ldap_server_uri: str
    ldap_base: str
    ldap_bind_dn: str
    ldap_bind_password: str

    udm_rest_api_base_url: str
    udm_rest_api_username: str
    udm_rest_api_password: str

    # The UDM REST API instance the udm-transformer reads from. It has its own
    # module cache, so a new extended attribute must reload there too before it
    # survives transformation. Empty falls back to the single instance above.
    udm_rest_api_transformer_base_url: str = ""

    @property
    def udm_rest_api_urls(self) -> list[str]:
        urls = [self.udm_rest_api_base_url]
        if self.udm_rest_api_transformer_base_url and self.udm_rest_api_transformer_base_url not in urls:
            urls.append(self.udm_rest_api_transformer_base_url)
        return urls

    @property
    def subscriptions_url(self) -> str:
        return urljoin(self.provisioning_api_base_url.rstrip("/") + "/", "v1/subscriptions")

    def subscriptions_messages_url(self, name: str) -> str:
        return f"{self.subscriptions_url}/{name}/messages"

    @property
    def messages_url(self) -> str:
        base_url = self.provisioning_api_base_url_primary or self.provisioning_api_base_url
        return urljoin(base_url.rstrip("/") + "/", "v1/messages")
