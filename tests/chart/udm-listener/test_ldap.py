# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

from univention.testing.helm.client.ldap import Auth, SecretViaVolume


class TestLdapClient(SecretViaVolume, Auth):
    config_map_name = "release-name-udm-listener"
    secret_name = "release-name-udm-listener-ldap"
    workload_kind = "StatefulSet"
    workload_name = "release-name-udm-listener"

    path_ldap_bind_dn = "data.LDAP_HOST_DN"
