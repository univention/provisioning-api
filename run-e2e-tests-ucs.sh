#!bin/bash
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


docker run \
    --rm \
    -it \
    --volume=e2e_settings_ucs.json:/app/e2e_tests/e2e_settings.json \
    --network=nubus-provisioning \
    gitregistry.knut.univention.de/univention/dev/projects/provisioning/provisioning-e2e-tests:0.63.0-pre-provisioning-in-ucs \
    pytest
