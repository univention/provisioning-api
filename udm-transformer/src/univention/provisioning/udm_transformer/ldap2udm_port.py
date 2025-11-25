# Callable | NoneSPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

from typing import Any, Optional

from .config import UDMTransformerSettings, udm_transformer_settings


class Ldap2Udm:
    def __init__(self, settings: Optional[UDMTransformerSettings] = None):
        self.settings = settings or udm_transformer_settings()

    def ldap_to_udm(self, entry: dict[str, Any]) -> dict[str, Any]: ...
