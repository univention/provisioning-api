#!/bin/bash

set -e

docker system prune -f
export PROVISIONING_API_ADMIN_PASSWORD=$(jq -r '.PROVISIONING_API_ADMIN_PASSWORD' /etc/provisioning-json.secrets)
export PROVISIONING_API_ADMIN_USER=admin
export PROVISIONING_API_URL=https://$(ucr get ldap/master)/univention/provisioning/
export NATS_USER=api
export NATS_PASSWORD=$(jq -r '.NATS_PASSWORD' /etc/provisioning-json.secrets)
export TARGET_NATS=nats://nats:4222
export PROVISIONING_API_BASE_URL="http://nubus-provisioning-api:7777"

mkdir -p secrets

echo "
services:
  test:
    image: gitregistry.knut.univention.de/univention/dev/projects/provisioning/backup-consumer:feat-provisioning-stack-listener-cleanup
    container_name: backup-consumer
    command: >
      backup_consumer
      --provisioning-api-admin-user "${PROVISIONING_API_ADMIN_USER}"
      --provisioning-api-admin-user-password "${PROVISIONING_API_ADMIN_PASSWORD}"
      --nats-user "${NATS_USER}"
      --nats-password "${NATS_PASSWORD}"
      --target-nats "${TARGET_NATS}"
      --provisioning-url ${PROVISIONING_API_URL}
      --stream-name "backup-4"
    environment:
      PROVISIONING_API_USERNAME: ${PROVISIONING_API_ADMIN_USERNAME}
      PROVISIONING_API_PASSWORD: ${PROVISIONING_API_ADMIN_PASSWORD}
      LOG_LEVEL: DEBUG
      PROVISIONING_API_BASE_URL: ${PROVISIONING_API_URL}
      MAX_ACKNOWLEDGEMENT_RETRIES: 5
    volumes:
      - /etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro
      - /var/lib/univention-appcenter/apps/provisioning-service/conf/server_role.conf:/server_role.conf:ro
    networks:
      nubus-provisioning:
networks:
  nubus-provisioning:
    external: true
" > client.yaml

docker-compose -f client.yaml pull
docker-compose -f client.yaml up
