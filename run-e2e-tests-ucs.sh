#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

#
# Temporary helper script to run e2e tests on a UCS host which has the Provisioning Service app
# already installed.
#
#
# Necessary manual steps:
#  - copy e2e_tests/e2e_settings_ucs.json to your UCS VM
#  - update the passwords in there:
#
#    e2e_settings_ucs.json              /etc/provisioning-secrets.json (on UCS VM)
#    ---------------------              ------------------------------------------
#    provisioning_admin_password   <--  PROVISIONING_API_ADMIN_PASSWORD
#    provisioning_events_password  <--  EVENTS_PASSWORD_UDM
#    nats_password                 <--  NATS_PASSWORD
#
#  - run this script from the directory where your `e2e_settings_ucs.json` is located.
#
apt update
apt install -y jq

provisioning_admin_password=$(sudo cat /etc/provisioning-secrets.json | jq -r '.PROVISIONING_API_ADMIN_PASSWORD')
provisioning_events_password=$(sudo cat /etc/provisioning-secrets.json | jq -r '.EVENTS_PASSWORD_UDM')
nats_password=$(sudo cat /etc/provisioning-secrets.json | jq -r '.NATS_PASSWORD')
host=$(ucr get ldap/server/name)
master_host=$(ucr get ldap/master)

cat <<EOF > e2e_settings_ucs.json
{
  "local": {
    "provisioning_api_base_url": "https://${host}/univention/provisioning",
    "provisioning_admin_username": "admin",
    "provisioning_admin_password": "$provisioning_admin_password",
    "provisioning_events_username": "udm",
    "provisioning_events_password": "$provisioning_events_password",
    "nats_url": "nats://nats:4222",
    "nats_user": "api",
    "nats_password": "$nats_password",
    "ldap_server_uri": "ldap://${host}:389",
    "ldap_base": "$(ucr get ldap/base)",
    "ldap_bind_dn": "uid=Administrator,cn=users,$(ucr get ldap/base)",
    "ldap_bind_password": "univention",
    "udm_rest_api_base_url": "https://${master_host}/univention/udm/",
    "udm_rest_api_username": "Administrator",
    "udm_rest_api_password": "univention"
  }
}
EOF
docker run \
    --rm \
    -it \
    --volume=$(pwd)/e2e_settings_ucs.json:/app/e2e_tests/e2e_settings.json \
    --volume=/var/www/ucs-root-ca.crt:/etc/ssl/certs/ca-certificates.crt:ro \
    --network=nubus-provisioning \
    --env=REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt \
    gitregistry.knut.univention.de/univention/dev/projects/provisioning/provisioning-e2e-tests:0.63.0-pre-provisioning-in-ucs \
    /bin/bash
#    pytest -v
