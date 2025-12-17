#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


set -e

if [[ $# -ne 2 ]] ; then
    echo 'Usage: run.sh <action> <kubernetes_namespace>'
    exit -1
fi

action="$1"
kubernetes_namespace="$2"

udm_url="https://$(kubectl -n "${kubernetes_namespace}" get ingress nubus-udm-rest-api --no-headers | awk '{ print $3}')/univention/udm"
udm_username="$(kubectl -n "${kubernetes_namespace}" get configmap nubus-udm-rest-api -o jsonpath='{.data.UDM_API_USER}')"
udm_password="$(kubectl -n "${kubernetes_namespace}" get secret nubus-ldap-server-admin -o jsonpath='{.data.password}' | base64 --decode)"

provisioning_username="admin"
provisioning_password="$(kubectl -n "${kubernetes_namespace}" get secret nubus-provisioning-api-admin -o jsonpath='{.data.password}' | base64 --decode)"
provisioning_base_url="http://localhost:20080"

ldap_base_dn="$(kubectl -n "${kubernetes_namespace}" get configmap nubus-ldap-server -o jsonpath='{.data.LDAP_BASE_DN}')"

echo "Namespace: ${kubernetes_namespace}"
echo "UDM URL: ${udm_url}"
echo "UDM username: ${udm_username}"
echo "UDM password: ${udm_password}"
echo "Provisioning server: ${provisioning_base_url}"
echo "Provisioning username: ${provisioning_username}"
echo "Provisioning password: ${provisioning_password}"
echo "LDAP base DN: ${ldap_base_dn}"

export LOG_LEVEL="DEBUG"
export UDM_URL="${udm_url}"
export UDM_USERNAME="${udm_username}"
export UDM_PASSWORD="${udm_password}"
export PROVISIONING_API_BASE_URL="${provisioning_base_url}"
export PROVISIONING_API_USERNAME="${provisioning_username}"
export PROVISIONING_API_PASSWORD="${provisioning_password}"
export KUBERNETES_NAMESPACE="${kubernetes_namespace}"
export LDAP_BASE_DN="${ldap_base_dn}"

if [ "${action}" == "queue" ]; then
    uv run test_queue
elif [ "${action}" == "attributes" ]; then
    uv run test_extended_attributes
fi
