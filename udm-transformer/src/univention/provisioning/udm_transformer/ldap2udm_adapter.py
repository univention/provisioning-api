# Callable | NoneSPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import base64
import logging
import urllib.parse
from typing import Optional

import dns.resolver
import requests

from univention.admin.rest.client import UDM, ServerError, UnprocessableEntity

from .config import UDMTransformerSettings
from .ldap2udm_port import Ldap2Udm

logger = logging.getLogger(__name__)


UDM_MODULES_RELOAD_TRIGGER = {
    "settings/extended_attribute",
}


class UdmRestApiError(Exception):
    pass


class Ldap2UdmAdapter(Ldap2Udm):
    def __init__(self, settings: Optional[UDMTransformerSettings] = None):
        Ldap2Udm.__init__(self, settings)
        self.udm_url = settings.udm_url
        self.udm_auth = (settings.udm_username, settings.udm_password)
        self.udm_needs_reload = settings.udm_needs_reload
        self.udm = UDM.http(self.udm_url, *self.udm_auth)

    def discover_pods_ips(self):
        # kubernetes magic
        hostname = urllib.parse.urlparse(self.udm_url).hostname
        udm_api_ips = dns.resolver.resolve(hostname, "A", search=True)
        return [ip.address for ip in udm_api_ips]

    def reload_udm_if_required(self, obj: dict) -> None:
        if not self.udm_needs_reload:
            return
        if obj.get("objectType") not in UDM_MODULES_RELOAD_TRIGGER:
            return
        logger.info("Reload of UDM modules triggered by change of %r object.", obj["objectType"])
        for ip in self.discover_pods_ips():
            # ATTENTION: credentials via HTTP. okay as this is meant to be done only inside "kubernetes VPN"
            (
                requests.get(
                    "http://%s/univention/udm/-/reload" % ip, auth=self.udm_auth, headers={"Accept": "application/json"}
                ),
            )

    def ldap_to_udm(self, entry: dict) -> dict:
        dn = entry["entryDN"][0].decode("utf-8")
        # the UDM REST API expects only base64 encoded attributes
        attributes = {k: [base64.b64encode(_v).decode("utf-8") for _v in v] for k, v in entry.items()}
        payload = {
            "dn": dn,
            "attributes": attributes,
        }

        try:
            return self.udm.client.request(
                "POST", self.udm.uri + "/directory/unmap-ldap-attributes", data=payload, expect_json=True
            )
        except UnprocessableEntity as exc:
            logger.error("Could not unmap LDAP attributes: %s ", exc)
            raise UdmRestApiError("ReadControl response suggests that UDM does not recognize the object!")
        except ServerError as exc:
            logger.error("Server error during unmapping LDAP attributes: %s ", exc)
            raise UdmRestApiError("ReadControl response points to a server error!")
