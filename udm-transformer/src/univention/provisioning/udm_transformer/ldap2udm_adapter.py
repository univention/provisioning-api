# Callable | NoneSPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import base64
import importlib
import logging
from typing import Optional

import requests

from .config import UDMTransformerSettings
from .ldap2udm_port import Ldap2Udm

logger = logging.getLogger(__name__)


class UdmRestApiError(Exception):
    pass


class Ldap2UdmAdapter(Ldap2Udm):
    def __init__(self, settings: Optional[UDMTransformerSettings] = None):
        Ldap2Udm.__init__(self, settings)
        if settings.ldap_bind_dn.startswith("cn=admin,"):
            udm_username = "cn=admin"
        else:
            udm_username = settings.ldap_bind_dn.split("=", 2)[0]
        self.udm_host = settings.udm_host
        self._auth = (udm_username, self.ldap_bind_pw)

    def ldap_to_udm(self, entry: dict) -> dict:
        dn = entry["entryDN"][0]
        # the UDM REST API expects only base64 encoded attributes
        attributes = {k: [base64.b64encode(_v) for _v in v] for k, v in entry.items()}
        payload = {
            "dn": dn,
            "attributes": attributes,
        }

        response = requests.post("https://%s/univention/udm/directory/unmap-ldap-attributes" % self.udm_host, json=payload, auth=self._auth)
        if response.ok:
            return response.json()
        if response.status_code == 500:
            logger.error("ReadControl response points to a server error!")
            response = response.json()
            traceback = response.get("error", {}).get("traceback")
            logger.error(traceback)
            raise UdmRestApiError("Could not fulfill the request")
        if response.status_code == 422:
            logger.error("ReadControl response suggests that UDM does not recognize the object!")
            return {}
        logger.error("ReadControl response returned %s. Cannot transform this object." % response.status_code)
        return {}
