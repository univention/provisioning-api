#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

set -euxo pipefail

ln --symbolic --force "${MACHINE_SECRET_FILE:-/run/secrets/machine_secret}" "/etc/machine.secret"

if [ ! -e /etc/machine.secret ]
then
    echo "ERROR: MACHINE_SECRET_FILE is not set correctly."
    exit 1
fi

# Ensure that the Python library "requests" does find the certificate
export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
