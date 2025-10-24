#!bin/bash

# Necessary manual step: copy e2e_tests/e2e_settings_ucs.json to your host


docker run \
    --rm \
    -it \
    --volume=~/e2e_settings_ucs.json:/app/e2e_tests/e2e_settings.json \
    --network=nubus-provisioning \
    gitregistry.knut.univention.de/univention/dev/projects/provisioning/provisioning-e2e-tests:0.63.0-pre-provisioning-in-ucs \
    pytest
