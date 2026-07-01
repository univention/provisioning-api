#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023-2025 Univention GmbH


# abort on nonzero exitstatus
set -o errexit
# abort on unbound variable
set -o nounset
# don't hide errors within pipes
set -o pipefail

exec "/usr/sbin/univention-directory-listener" \
  -F \
  -x \
  -d "${DEBUG_LEVEL}" \
  -b "${LDAP_BASE_DN}" \
  -D "cn=admin,${LDAP_BASE_DN}" \
  -n "${NOTIFIER_SERVER}" \
  -m "/usr/lib/univention-directory-listener/system" \
  -c "/var/lib/univention-directory-listener" \
  -y "${LDAP_PASSWORD_FILE}" -Z

# [EOF]
