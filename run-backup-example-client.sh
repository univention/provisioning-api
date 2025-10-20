#!/bin/bash

set -e

docker system prune -f
export PROVISIONING_API_ADMIN_PASSWORD=$(jq -r '.PROVISIONING_API_ADMIN_PASSWORD' /etc/provisioning-secrets.json)
export PROVISIONING_API_ADMIN_USER=admin
export PROVISIONING_API_URL=https://$(ucr get ldap/master)/univention/provisioning/v1/subscriptions

mkdir -p secrets

echo '
{
  "name": "example-client",
  "realms_topics": [
    {
      "realm": "udm",
      "topic": "users/user"
    },
    {
      "realm": "udm",
      "topic": "groups/group"
    }
  ],
  "request_prefill": true,
  "password": "password"
}
' > secrets/example-client-registration-payload.json 

curl -v -X POST --user "${PROVISIONING_API_ADMIN_USER}:${PROVISIONING_API_ADMIN_PASSWORD}" -H "Content-Type: application/json" --data @./secrets/example-client-registration-payload.json $PROVISIONING_API_URL

echo '
services:
  example-client:
    image: "artifacts.software-univention.de/nubus/images/provisioning-example-client:0.48.0"
    container_name: "nubus-provisioning-example-client"
    environment:
        LOG_LEVEL: DEBUG
        PROVISIONING_API_USERNAME: "example-client"
        PROVISIONING_API_PASSWORD: "password"
        PROVISIONING_API_BASE_URL: "http://nubus-provisioning-api:7777"
        LOG_LEVEL: "DEBUG"
        MAX_ACKNOWLEDGEMENT_RETRIES: 3
    restart: "on-failure"
    networks:
      - nubus-provisioning
networks:
  nubus-provisioning:
    external: true
' > client.yaml

docker-compose -f client.yaml up
