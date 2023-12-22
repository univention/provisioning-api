#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

set -euxo pipefail
shopt -s expand_aliases

alias tsecho='echo "$(date --utc +%Y-%m-%dT%H:%M:%SZ)"'

if [[ ! -d "/var/lib/univention-ldap/listener/" ]]; then
  tsecho "The listener dir is missing!"
  tsecho "It should be a shared volume with the OpenLDAP container."
  exit 2
fi

if [[ ! -d "/var/run/slapd/" ]]; then
  tsecho "The slapd run dir is missing!"
  tsecho "It should be a shared volume with the OpenLDAP container."
  exit 3
fi

mkdir --parents /var/lib/univention-ldap/notify

# The notifier writes an error message to its log-file if this file is missing.
# Because it lives in a volume, it can not be created during build.
touch /var/lib/univention-ldap/notify/transaction

# Both notifier and slapd need to be able to write this lock-file.
# The slapd writes to it on db-change, not on startup.
# The notifier writes to it whenever data is found in the "listener"-file.
touch /var/lib/univention-ldap/listener/listener.lock

# Wait for the openldap container to create ldapi and translog file
tsecho "Check for the listener and ldapi files:"
cur_backoff_seconds=1
max_backoff_seconds=512
while [[ ! -e "/var/lib/univention-ldap/listener/listener" ]] &&
    [[ ! -e "/var/run/slapd/ldapi" ]]; do
  if [[ cur_backoff_seconds -ge max_backoff_seconds ]]; then
    tsecho "Waited for too long"
    exit 4
  fi
  tsecho -n "Retrying in ${cur_backoff_seconds} seconds"
  sleep "${cur_backoff_seconds}"
  (( cur_backoff_seconds*=2 )) || true
done
tsecho "Found the needed files"

# Check for pending transations
transaction_path='/var/lib/univention-ldap/notify/transaction'
if [[ -s "${transaction_path}" ]]; then
  tsecho "Found pending transactions"
  last_id="$(awk 'END{print $1}' "${transaction_path}")"
  tsecho "Last transaction: ${last_id}"
  translog_result=0
  /usr/share/univention-directory-notifier/univention-translog ldap "$last_id" \
    || translog_result="$?"
  if [[ "${translog_result}" -gt "1" ]]; then
    tsecho "Bad translog result: ${translog_result}"
    exit 5
  elif [[ "${translog_result}" -eq "1" ]]; then
    tsecho "Importing from translog to LDAP"
    /usr/share/univention-directory-notifier/univention-translog --lenient import
  fi
fi

exec "$@"

# [EOF]
